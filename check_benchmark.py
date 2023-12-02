#check benchmark.yaml integrity

import hashlib
import platform

file_url = 'benchmark.yaml'

# public
def calc_benchmark_hash(hash_algorithm="sha256"):
    '''
    Calculate the hash of a file using the specified hash algorithm.
    '''
    hasher = hashlib.new(hash_algorithm)
    with open(file_url, "rb") as file:
        while True:
            data = file.read(65536)  # Read the file in 64KB chunks.
            if not data:
                break
            hasher.update(data)
    if platform.system() == 'Darwin':
        return(hasher.hexdigest().lower() == 'b3e6e452e2730eb3efb64b0422def0625b3804661eda25d29411374ec1881371')
    elif platform.system() == 'Windows':
        return(hasher.hexdigest().lower() == 'ef90234a6c559085ff3994f0fcb25085f2e297daf99c59fae6f153c67c5707e5')
    else:
        return(False)
