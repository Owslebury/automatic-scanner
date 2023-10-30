import subprocess

def scan_without_console_output():
    with open('output.txt', 'w') as outfile:
        with subprocess.Popen(["python", "scanner_animator.py"], stdout=outfile, stderr=outfile) as process:
            process.communicate()

if __name__ == "__main__":
    scan_without_console_output()

