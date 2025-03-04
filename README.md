
░█▀▀▄░█░▒█░▀█▀░▄▀▀▄░░░▀▀█▀▀░█▀▀▄░█▀▄▀█░▄▀▀▄░█▀▀░█▀▀▄
▒█▄▄█░█░▒█░░█░░█░░█░░░░▒█░░░█▄▄█░█░▀░█░█▄▄█░█▀▀░█▄▄▀
▒█░▒█░░▀▀▀░░▀░░░▀▀░░░░░▒█░░░▀░░▀░▀░░▒▀░█░░░░▀▀▀░▀░▀▀

## AutoTamper - Automatic SQLMap Tamper Tester

AutoTamper is an automatic tamper test tool using SQLMap. It allows you to input a target URL with an injection point and a set of SQLMap command options. The tool then runs SQLMap with various tamper scripts to identify which tamper script works best with your target.

### 🚀 How to Use

1. Download `auto.py` and place it inside your `sqlmap` folder (next to `sqlmap.py`).
2. Open a terminal and navigate to the `sqlmap` directory.
3. Run the script:
   ```bash
   python auto.py
   ```
4. Enter the target URL and SQLMap command when prompted.
5. The tool will automatically test different tamper scripts and suggest the best one for your target.

📌 Note: Make sure you have SQLMap installed and your tamper/ folder contains valid tamper scripts.

