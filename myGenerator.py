import re
import codecs
from pathlib import Path
from Preprocess_RawData import Preprocess_CoCoNut_fromRaw
from translate import translate_CoCoNut
from Utils.IOHelper import readF2L
from CoCoNut.tokenization.tokenization import get_strings_numbers, token2statement
# from Recovery_Code import Recovery_CoCoNut_all

rawDataDirPath = Path('/home/yicheng/check-apr/dataset/ids_info')

mutInfoDict = {'chart': { 'AOR': [164,165,166,167,170,171,172,173,204,205,206,207,212,213,214,215,371,372,373,374,395,396,397,398,400,401,402,403,404,405,406,407,409,410,411,412,413,414,415,416,428,429,430,431,434,435,436,437], 
                    'COR': [16,17,22,23,31,32,37,38,45,46,51,52,56,57,60,61,85,86,108,109,110,111,117,118,124,125,138,139,153,154,183,184,198,199,224,225,226,227,231,232,235,236,241,242,245,246,263,264,265,266,281,282,284,285,287,288,290,291,293,294,296,297,299,300,302,303,305,306,308,309,311,312,318,319,325,326,330,331,333,334,358,359,365,366,380,381,390,391], 
                    'LOR': [64,65], 
                    'LVR': [7,8,13,19,28,34,42,48,78,79,80,81,89,90,91,92,99,100,102,103,115,119,120,147,148,279,280,283,286,289,292,295,298,301,304,307,310,313,336,337,360,361,369,370,375,376,385,386,387,388,393,394,426,427,432,433,438,439,440,441,444], 
                    'ROR': [9,11,26,40,55,71,82,83,84,96,106,107,112,116,121,122,123,129,130,131,133,140,142,149,150,151,155,157,163,169,178,186,188,193,201,209,217,222,223,228,249,254,256,258,260,262,267,269,272,278,314,316,317,322,339,341,343,345,347,349,354,356,357,362,363,364,367,377,378,379,382,384,392,399,418,420,423,425,443], 
                    'STD': [1,2,3,4,5,6,10,12,14,15,18,20,21,24,25,27,29,30,33,35,36,39,41,43,44,47,49,50,53,54,58,59,62,63,66,67,68,69,70,72,73,74,75,76,77,87,88,93,94,95,97,98,101,104,105,113,114,126,127,128,132,134,135,136,137,141,143,144,145,146,152,156,158,159,160,161,162,168,174,175,176,177,179,180,181,182,185,187,189,190,191,192,194,195,196,197,200,202,203,208,210,211,216,218,219,220,221,229,230,233,234,237,238,239,240,243,244,247,248,250,251,252,253,255,257,259,261,268,270,271,273,274,275,276,277,315,320,321,323,324,327,328,329,332,335,338,340,342,344,346,348,350,351,352,353,355,368,383,389,408,417,419,421,422,424,442] }, 
                'lang': { 
                    'AOR': [80,81,82,83,128,129,130,131,132,133,134,135,138,139,140,141,166,167,168,169,172,173,174,175,203,204,205,206,216,217,218,219,222,223,224,225,230,231,232,233,296,297,298,299,309,310,311,312,363,364,365,366,416,417,418,419,690,691,692,693,706,707,708,709,719,720,721,722,776,777,778,779], 
                    'COR': [58,59,62,63,97,98,99,100,101,102,103,104,118,119,120,121,122,123,124,125,160,161,162,163,192,193,194,195,210,211,212,213,234,235,236,237,240,241,242,243,251,252,253,254,255,256,257,258,259,260,261,262,268,269,270,271,272,273,274,275,281,282,283,284,285,286,287,288,303,304,305,306,315,316,317,318,319,320,321,322,333,334,335,336,337,338,339,340,351,352,353,354,355,356,357,358,391,392,398,399,400,401,408,409,423,424,425,426,431,432,434,435,436,437,494,495,508,509,570,571,584,585,660,661,668,669,672,673,700,701,702,703,713,714,715,716,736,737,738,739,746,747,748,749,750,751,752,753,760,761,762,763,764,765,766,767,783,784,785,786,787,788,789,790,791,792,793,794,801,802,803,804,812,813,814,815,825,826,827,828,829,830,832,833,845,846,847,848,849,850,867,868,869,870,878,879,880,881,886,887,888,889,897,898,899,900,904,905,906,907,911,912,913,914,915,916,917,918,925,926,927,928,929,930,931,932,933,934,935,936,938,939,940,941], 
                    'LVR': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,30,31,32,33,34,35,37,38,39,40,42,43,45,46,48,49,51,52,54,55,60,61,65,66,70,71,84,85,89,90,105,106,110,111,126,127,136,137,142,143,144,145,149,150,164,165,170,171,176,177,179,180,187,188,196,197,201,202,214,215,220,221,226,227,228,229,244,245,249,250,263,264,276,277,289,290,294,295,307,308,323,324,328,329,341,342,346,347,360,361,362,367,368,375,376,377,386,387,388,389,390,393,395,396,402,403,405,406,410,411,414,415,427,428,439,440,441,442,451,452,453,454,463,464,465,466,475,476,477,478,487,488,489,490,501,502,503,504,515,516,517,518,527,528,529,530,539,540,541,542,551,552,553,554,563,564,565,566,577,578,579,580,591,592,662,663,664,670,671,674,675,676,677,678,679,680,684,685,686,687,688,689,704,705,717,718,726,768,769,774,775,805,807,816,817,831,834,835,837,851,852,854,856,871,882,890,937], 
                    'ORU': [29,36], 
                    'ROR': [41,44,47,50,53,56,57,67,68,69,72,73,74,76,77,78,86,87,88,91,92,93,94,95,96,107,108,109,112,113,114,115,116,117,146,147,148,151,152,153,154,155,156,157,158,159,181,182,183,184,185,186,189,190,191,198,199,200,207,208,209,238,239,246,247,248,265,266,267,278,279,280,291,292,293,300,301,302,313,314,325,326,327,330,331,332,343,344,345,348,349,350,359,369,370,371,372,373,374,378,379,380,381,382,383,384,385,420,421,422,433,443,444,445,446,447,448,455,456,457,458,459,460,467,468,469,470,471,472,479,480,481,482,483,484,491,492,493,496,497,498,505,506,507,510,511,512,519,520,521,522,523,524,531,532,533,534,535,536,543,544,545,546,547,548,555,556,557,558,559,560,567,568,569,572,573,574,581,582,583,586,587,588,590,593,594,595,596,597,598,600,601,602,604,605,606,608,609,610,612,613,614,616,617,618,620,621,622,624,625,626,628,629,630,632,633,634,636,637,638,640,641,642,644,645,646,648,649,650,652,653,654,656,657,658,665,666,667,681,682,683,694,695,696,697,698,699,710,711,712,723,724,725,727,728,729,730,731,732,733,734,735,740,741,742,743,744,745,754,755,756,757,758,759,771,772,773,780,781,782,795,796,797,798,799,800,809,810,811,819,820,821,822,823,824,839,840,841,842,843,844,858,859,860,861,862,863,864,865,866,872,873,874,875,876,877,883,884,885,891,892,893,894,895,896,901,902,903,908,909,910,919,920,921,922,923,924], 
                    'STD': [64,75,79,178,394,397,404,407,412,413,429,430,438,449,450,461,462,473,474,485,486,499,500,513,514,525,526,537,538,549,550,561,562,575,576,589,599,603,607,611,615,619,623,627,631,635,639,643,647,651,655,659,770,806,808,818,836,838,853,855,857]}}

# def Preprocess_CoCoNut_fromRaw(ids_f,input_dir,temp_prefix,output_dir,src_dict_f,tgt_dict_f,mode,src_lang="buggy",tgt_lang="fix"):
# ids_f: id list
# input_dir: needed buggy_methods buggy_lines fix_lines
# temp_prefix: a directory which stores the processed raw data file
# output_dir: a directory that stores the compressed data file (fairseq data form)
# src_dict_f: dictionary for buggy codes
# tgt_dict_f: dictionary for fix codes

def preprocess(project: str):  # 'chart' or 'lang'
    ids_f = str(rawDataDirPath / (project + '.ids'))
    input_dir = str(rawDataDirPath)
    temp_prefix = str(rawDataDirPath / (project + '-temp'))
    output_dir = str(rawDataDirPath / ('output-' + project))
    src_dict_f = '/home/yicheng/check-apr/NPR4J/models/CoCoNut_Trained/dict.ctx.txt'
    tgt_dict_f = '/home/yicheng/check-apr/NPR4J/models/CoCoNut_Trained/dict.fix.txt'
    Preprocess_CoCoNut_fromRaw(ids_f,input_dir,temp_prefix,output_dir,src_dict_f,tgt_dict_f,'test',src_lang="buggy",tgt_lang="fix")

# def predict(project: str):  # 'chart' or 'lang'
#     translate_CoCoNut()

def recovery(project: str, preds_f: str):
    ids_f = str(rawDataDirPath / (project + '.ids'))
    buggy_lines_dir = str(rawDataDirPath / 'buggy_lines')
    buggy_classes_dir = str(rawDataDirPath / 'buggy_classes')
    buggy_methods_dir = str(rawDataDirPath / 'buggy_methods')
    output_dir_path = rawDataDirPath / 'patches' / Path(preds_f).stem
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_dir = str(output_dir_path)

    Recovery_CoCoNut_all(preds_f,ids_f,buggy_lines_dir,buggy_methods_dir,buggy_classes_dir,output_dir,candi_size=300)


def Recovery_CoCoNut_one(buggy_file,pred_str):
    # strings,numbers=get_strings_numbers(buggy_str)
    strings,numbers=get_strings_numbers_from_file(buggy_file)
    recovery_tokens=pred_str.split()
    recovery_str=token2statement(recovery_tokens,numbers,strings)
    #print(recovery_str)
    if len(recovery_str)==0:
        recovery_str=[pred_str]
    return recovery_str

def get_strings_numbers_from_file(file_path):
    numbers_set = set()
    strings_set = set()
    with open(file_path, 'r') as file:
        data = file.readlines()
        for idx, line in enumerate(data):
            strings, numbers = get_strings_numbers(line)
            numbers_set.update(numbers)
            strings_set.update(strings)
    return list(strings_set), list(numbers_set)

def Recovery_CoCoNut_all(preds_f,ids_f,buggy_lines_dir,buggy_methods_dir,buggy_classes_dir,output_dir,candi_size=100):
    ids=readF2L(ids_f)
    preds=readF2L(preds_f)
    assert len(preds) % (candi_size + 2) == 0
    ind_list = list(range(0, len(preds), (candi_size+2)))
    for i in ind_list:
        group = preds[i:i+candi_size+2]
        idx= group[2].split('\t')[0]
        idx=int(idx[2:])
        id=ids[idx]
        id_buggyline=codecs.open(buggy_lines_dir+'/'+id+'.txt','r',encoding='utf8').read().strip()
        id_buggymethod=codecs.open(buggy_methods_dir+'/'+id+'.txt','r',encoding='utf8').read()
        # patches_dict=dict()
        patchedLines = []
        for pid,pred in enumerate(group[2:]):
            pred=pred.split('\t')[-1]
            # rec_line=Recovery_CoCoNut_one(id_buggyline,pred)
            rec_lines=Recovery_CoCoNut_one(buggy_classes_dir+'/'+id+'.java',pred)
            patchedLines.extend(rec_lines)
            # rec_method=id_buggymethod.replace(id_buggyline,rec_line)
            # patches_dict[str(pid)]=rec_method
        with open(output_dir+'/'+id+'.txt','w',encoding='utf8')as f:
            # json.dump(patches_dict,f,indent=2)
            for line in patchedLines:
                f.write(line + '\n')
            f.close()
        print(i)
    print('='*100)


def translateAllCoconut():
    for i in [5, 7, 9, 12, 15, 21, 32, 33, 35, 99]:
        for project in ['chart', 'lang']:
            print('=' * 10 + 'CoCoNut-{}-{}'.format(i, project) + '=' * 10)
            translate_CoCoNut('/home/yicheng/check-apr/dataset/ids_info/config/CoCoNut-{}-{}.yaml'.format(i, project), False)

def checkCorrectlyFixedMutants():
    fixedmutIds = set()
    fixLinesDirPath = rawDataDirPath / 'fix_lines'
    patchesDirPath = rawDataDirPath / 'patches'
    for file in fixLinesDirPath.iterdir():
        fileName = file.name
        with file.open() as f:
            fixedStr = ''.join(f.read().split())
            # print(fixedStr)
        foundCorrectFix = False
        for modelPatchDir in patchesDirPath.iterdir():
            modelPatchFile = modelPatchDir / fileName
            if modelPatchFile.exists():
                with modelPatchFile.open() as p:
                    for line in p:
                        tmp = ''.join(line.split())
                        if tmp == fixedStr:
                            # print('Found fix!')
                            fixedmutIds.add(file.stem)
                            foundCorrectFix = True
                            break
            if foundCorrectFix:
                break
    print('Fixed Mutants: ' + str(fixedmutIds))
    fixedChartIds = []
    fixedLangIds = []
    for id in fixedmutIds:
        m = re.match(r'\w+?(\d+)', id)
        if 'chart' in id:
            fixedChartIds.append(int(m[1]))
        elif 'lang' in id:
            fixedLangIds.append(int(m[1]))
    print('Fixed Chart Mutants: ' + str(fixedChartIds))
    print('len(fixedChartIds): ' + str(len(fixedChartIds)))
    calculateFixedMutatorNum('chart', fixedChartIds)
    print('Fixed Lang Mutants: ' + str(fixedLangIds))
    print('len(fixedLangIds): ' + str(len(fixedLangIds)))
    calculateFixedMutatorNum('lang', fixedLangIds)

def calculateFixedMutatorNum(projectName: str, fixedProjIds):
    assert projectName in mutInfoDict
    print('='*5 + projectName + '='*5)
    for mutator in mutInfoDict[projectName]:
        fixedNum = 0
        for id in mutInfoDict[projectName][mutator]:
            if id in fixedProjIds:
                fixedNum += 1
        print('{}: {}'.format(mutator, fixedNum))

if __name__ == '__main__':
    # translateAllCoconut()
    # preprocess('chart')
    # preprocess('lang')
    translate_CoCoNut('/home/yicheng/check-apr/dataset/ids_info/config/CoCoNut-5-chart-test.yaml', False)
    # Recovery_CoCoNut_all(preds_f,ids_f,buggy_lines_dir,buggy_methods_dir,output_dir,candi_size=100)

    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-5-chart.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-12-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-12-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-15-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-15-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-21-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-21-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-32-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-32-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-33-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-33-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-35-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-35-lang.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-5-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-7-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-7-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-9-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-9-lang.pred')
    # recovery('chart', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-99-chart.pred')
    # recovery('lang', '/home/yicheng/check-apr/dataset/ids_info/prediction/CoCoNut-99-lang.pred')
    # checkCorrectlyFixedMutants()