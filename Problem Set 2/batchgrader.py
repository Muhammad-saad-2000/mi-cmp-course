import os, subprocess, argparse
from posixpath import dirname

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("out")
    parser.add_argument("--repeat", "-r", type=int, default=4)
    args = parser.parse_args()

    path: str = args.path
    out: str = args.out
    repeat: int = args.repeat
    
    dirnames = [dirname for dirname in os.listdir(path) if os.path.isdir(os.path.join(path, dirname))]    
    results = {dirname:[] for dirname in dirnames}

    environ = os.environ.copy()
    environ['PYTHONIOENCODING'] = 'utf-8'

    for r in range(1, repeat+1):
        for index, dirname in enumerate(dirnames):
            dirpath = os.path.join(path, dirname)
            print(f"Run #{r}/{repeat}: Grading Student {index+1}/{len(dirnames)} - {dirname}")
            result = subprocess.call(["python", "autograder.py", "-s", dirpath], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, encoding="utf-8", env=environ)
            results[dirname].append(result)
            print(f"Result:", result)
    
    with open(out, 'w') as f:
        f.writelines([f"{k}, {', '.join(str(v) for v in vs)}\n" for k, vs in results.items()])