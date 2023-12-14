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
        return(hasher.hexdigest().lower() == '9348ca05137c785ec209ec626d62f3da18294bb1f8d3f3c616bb0a8a2b4f73c4')
    elif platform.system() == 'Windows':
        return(hasher.hexdigest().lower() == '9348ca05137c785ec209ec626d62f3da18294bb1f8d3f3c616bb0a8a2b4f73c4')
    else:
        return(False)
