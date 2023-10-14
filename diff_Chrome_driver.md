How to use a different Chrome Driver?

By default, we automatically download the appropriate Chrome Driver for your system and store it in the `build/` directory. However, if you prefer to use a different version, please follow these instructions based on your operating system:

**Mac/Linux:**
1. First, navigate to the `build/` directory where the previously downloaded chromedriver is located.
   ```
   cd build/
   ```

2. Delete the existing downloaded chromedriver file created by the program.
   ```
   rm -rf chromedriver
   ```

3. Now, copy the desired chromedriver into the `build/` directory and name it as `chromedriver`.

4. Run `main.py`, and the manually pasted Chrome Driver will be used for your program.

**Windows:**
1. First, navigate to the `build/` directory where the previously downloaded chromedriver is located.
   ```
   cd build/
   ```

2. Delete the existing downloaded chromedriver file created by the program.
   ```
   del chromedriver.exe
   ```

3. Now, copy the desired chromedriver into the `build/` directory and name it as `chromedriver.exe`.

4. Run `main.py`, and the manually pasted Chrome Driver will be used for your program.
