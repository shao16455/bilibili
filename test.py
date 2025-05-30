import multiprocessing
import os
#启动脚本
def run_script(script_name):
    os.system(f"python {script_name}")

if __name__ == "__main__":
    scripts = ["src/main.py", "tests/loading.py", "tests/test_spider.py"]

    processes = []
    for script in scripts:

        process = multiprocessing.Process(target=run_script, args=(script,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()