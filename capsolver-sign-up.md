### ❓ How to create Capsolver Account to solve captcha's?

To simplify the captcha-solving process using CapSolver and save both time and effort, please follow these steps:

1. Start by creating a CapSolver account. Visit [capsolver.com](https://dashboard.capsolver.com/passport/register?inviteCode=lvdYBC4sYKRm) to sign up.

   ![Sign Up](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/sign-up-capsolver.png)

2. After setting up your account, the next step involves funding it. CapSolver allows you to add funds via various payment methods including PayPal and cryptocurrencies. Also, the minimum deposit is $6, and depending on your location, taxes ranging from 12% to 18% will apply.

   ![Add Funds](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/put-funds.gif)

3. After funding your account, copy your unique API Key. This key will help us in integrating CapSolver with your projects.

   ![Store API Key](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/copy-api-key.png)

4. With your account ready and API Key in hand, you can now easily automate captcha solving. Below is an example Python code snippet demonstrating how to use CapSolver for automatic captcha solving:

```python
from botasaurus import *
from capsolver_extension_python import Capsolver

@browser(
    extensions=[Capsolver(api_key="CAP-MY_KEY")], # Ensure to replace "CAP-MY_KEY" with your actual CapSolver API Key
)  
def solve_captcha(driver: AntiDetectDriver, data):
    driver.get("https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php")
    driver.prompt()

solve_captcha()
```

Please note that the sign-up link provided is an affiliate link. By using this link, you'll be able to support our project at no extra cost to you :)