
from Preprocess_RawData import preprocess_SequenceR_fromRaw
from Preprocess_RawData import Preprocess_PatchEdits_fromSequenceR
from pathlib import Path


# """
# ids_f: a list of bug-fix ids
# input_dir: raw data dir 
# output_dir: where you want to output the processed code of SequenceR
# tmp_dir: when building a SequenceR-type context, you need a directory to restore temp files
# """
#preprocess_SequenceR_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                             #"/home/zhongwenkang/RawData_Processed/SequenceR/bears","/home/zhongwenkang/RawData_Processed/SequenceR/temp")

dataDirPath = Path('ids_all_info').resolve()

def useSequencerPreprocessData():
    seqrPath = (dataDirPath / 'SequenceR').resolve()
    seqrPath.mkdir(exist_ok=True)
    preprocess_SequenceR_fromRaw(str(dataDirPath / 'sample_distribution+time2.ids'), str(dataDirPath), str(dataDirPath / 'SequenceR' / 'mutBench'), str(dataDirPath / 'SequenceR' / 'temp'))
    return seqrPath

#Preprocess_PatchEdits_fromSequenceR(r"D:\RawData_Processed\SequenceR\qbs.sids",r"D:\RawData_Processed\SequenceR\qbs.buggy",
                                    #r"D:\RawData_Processed\SequenceR\qbs.fix",r"D:\RawData_Processed\PatchEdits\qbs.data",
                                    #r"D:\RawData_Processed\PatchEdits\qbs.ids")

def preprocessForEditFromSequencerRawData(seqrPath: Path):
    editsPath = (dataDirPath / 'edits').resolve()
    editsPath.mkdir(exist_ok=True)
    Preprocess_PatchEdits_fromSequenceR(str(seqrPath / 'mutBench.sids'), str(seqrPath / 'mutBench.buggy'), str(seqrPath / 'mutBench.fix'), str(editsPath / 'mutBench.data'), str(editsPath / 'mutBench.ids'))

    # editsRepoPath = Path('/home/yicheng/research/mutBench/edits')
    # shutil.copyfile(str(editsRepoPath / 'data/model/'))
    heldOutFile = editsPath / 'heldout_keys.txt'
    testKeyFile = editsPath / 'test_keys.txt'
    with heldOutFile.open(mode='w'): pass
    with testKeyFile.open(mode='w') as f:
        f.write('test\n')


# Firstly use the sequencer preprocessing script to preprocess data
seqrPath = useSequencerPreprocessData()
# Then preprocess the data preprocessed by sequncer for edit
preprocessForEditFromSequencerRawData(seqrPath)