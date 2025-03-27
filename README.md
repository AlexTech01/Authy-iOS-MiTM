# Authy-iOS-MiTM
Guide to extract authenticator tokens from the Authy iOS app with mitmproxy

## Requirements
-A computer (Windows/Mac/Linux)

-An iOS/iPadOS device (using a secondary device is recommended)

-A basic understanding of the command line and running Python scripts

## Step 1: Setting up mitmproxy
Extracting tokens works by capturing HTTPS traffic received by the Authy app after logging in. This traffic contains your tokens in encrypted form, which is then decrypted in a later step so that you can access your authenticator seeds. In order to receive this traffic, we use mitmproxy, which is an easy-to-use tool that allows you to intercept traffic from apps and websites on your device.

To begin, install [mitmproxy](https://www.mitmproxy.org) on your computer, then run `mitmweb --allow-hosts "api.authy.com"` in your terminal to launch mitmweb (which is a user-friendly interface for mitmproxy) with HTTPS proxying on for "api.authy.com". Once proxying has started, connect your iOS device to the proxy by going to Settings -> Wi-Fi -> (your network) -> Configure Proxy, set it to "Manual", then enter your computer's private IP for "Server" and 8080 for "Port".

> [!NOTE]
> Your computer's private IP can be found in its Wi-Fi/network settings, and is typically in the format "192.168.x.x" or "10.x.x.x".

Once your iOS device is connected to the proxy, you'll need to install the mitmproxy root CA, which is required for HTTPS proxying. The root CA keys mitmproxy uses is randomly generated for each installation and is not shared. To install the root CA on your iOS device, visit `mitm.it` in Safari with the proxy connected, then tap "Get mitmproxy-ca-cert.pem" under the iOS section. Tap "Allow" on the message from iOS asking to install a configuration profile, then go to Settings, tap the "Profile Downloaded" message, and confirm installing the profile. **This may seem like the end, but it's not.** After the certificate is installed, you must allow root trust for it in Settings -> General -> About -> Certificate Trust Settings in order for it to work on websites and apps. Failure to do this step will result in Authy failing with an SSL validation error.

At this point, you have completed the process of setting up mitmproxy to capture HTTPS traffic from your iOS device. Keep the proxy connected for the next step, which is dumping tokens received from the Authy iOS app.

## Step 2: Dumping tokens
> [!NOTE]
> In order for this to work, you must have your Authy tokens synced to the cloud and you must have a backup password set. It is recommended to dump tokens with a secondary device in case something goes wrong.

> [!WARNING]
> If you're only using Authy on a single device, don't forget to [enable Authy multi-device](https://help.twilio.com/articles/19753646900379-Enable-or-Disable-Authy-Multi-Device) before logging out. If you don't, you won't be able to login back into your account and you will have to wait 24 hours for Twilio to recover it.

The first step in dumping tokens is to sign out of the Authy app on your device. Unfortuntely, Twilio did not implement a "sign out" feature in the app, so you must delete and reinstall the Authy app from the App Store if you are already signed in. With the proxy connected, sign back in to the app normally (enter your phone number and then authenticate via SMS/phone call/existing device), and then stop once the app asks you for your backup password.

> [!NOTE]
> If you get an "attestation token" error, try opening the Authy app with the proxy disconnected, enter your phone number, and then connect to the proxy before you tap on SMS/phone call/existing device verification.

At this point, mitmproxy should have logged your authenticator tokens in encrypted form. To find your tokens, simply search for "authenticator_tokens" in the "Flow List" tab of the mitmweb UI, then look at the "Response" of each request shown until you see something that looks like this:

`{ "authenticator_tokens": [ { "account_type": "example", "digits": 6, "encrypted_seed": "something", "issuer": "Example.com", "key_derivation_iterations": 100000, "logo": "example", "name": "Example.com", "original_name": "Example.com", "password_timestamp": 12345678, "salt": "something", "unique_id": "123456", "unique_iv": null }, ...`

Obviously, yours will show real information about every token you have in your Authy account. Once you find this request, switch to the "Flow" tab in mitmweb, then hit "Download" to download this data into a file called "authenticator_tokens". Rename this file to "authenticator_tokens.json" and disconnect your device from the proxy (select "Off" in Settings -> Wi-Fi -> (your network) -> Configure Proxy) before exiting out of the proxy on your computer (hit Ctrl+C on the terminal window running mitmweb) and continuing to the next step.

## Step 3: Decrypting tokens
You now have an authenticator_tokens.json file with your tokens in it, but it's encrypted and can't be used. Luckily, this file can be decrypted with your backup password and a Python script. Download the "decrypt.py" file in this repo, make sure your authenticator_tokens.json file is in the same folder as decrypt.py, and then run the Python script with `python3 decrypt.py`.

> [!NOTE]
> If you get an error that python3 couldn't be found, install Python on your computer from [python.org](https://www.python.org). If you get an error that the "cryptography" package couldn't be found, install it with `pip3 install cryptography`.

The script will prompt you for your backup password, which does not show in the terminal for privacy reasons. After entering your password and hitting Enter, you should have a decrypted_tokens.json file, which contains the decrypted authenticator seeds from your Authy account. Please note that this JSON file is not in a standard format that you can import to other authenticator apps, however some people have made scripts to convert the decrypted_tokens.json file into a format recognizable by other authenticator apps. I'll leave a link to some of these below.

## UPDATE: How to Use the Enhanced 2FA Converter Script

> Hi everyone! I've updated the Python script to be even more versatile. Now you can choose your target authenticator app and generate QR codes in a dedicated folder. Here's how to use it:

**What you need:**

-   **Python:** Download and install Python from [python.org](https://www.python.org). Make sure it's Python 3.13.1 or higher.
-   **Your 2FA data:** You'll need a file named `data.json`. Make a copy of your `decrypted.json` file and rename it to `data.json`. Put it in the same folder as the script.
-   **The script:** I added a file called `script.py` to this repository.

**Steps:**

1.  **Install Pillow and qrcode:**

    -   Open your computer's command line (or terminal).
    -   Type `pip install Pillow qrcode` and press Enter.

2.  **Put your files together:**

    -   Make sure `script.py` and `data.json` are in the same folder.

3.  **Run the script:**

    -   In the command line, go to the folder where you put the files.
    -   Type `python script.py` and press Enter.

4.  **Select your authenticator app:**

    -   The script will display a list of supported apps (Aegis, Google Authenticator, Microsoft Authenticator, 2FA).
    -   Enter the number corresponding to your desired app.

5.  **See the URIs:**

    -   The script will show you a list of your 2FA codes in a special format, tailored to your chosen app.

6.  **Make QR codes (optional):**

    -   The script will ask: "Generate QR codes? (Y/n):"
    -   Type `Y` and press Enter if you want QR codes.
    -   The script will create a new folder named "Generated QR Codes into .png" and save the QR code image files (like `GitHub_AhmadMorningstar.png`) inside.

That's it!

This script now provides more flexibility and organization for your 2FA data conversion. I hope it helps!


> [!NOTE]
> If you see "Decryption failed: Invalid padding length" as the decrypted_seed in your JSON file, you entered an incorrect backup password. Run the script again with the correct backup password.

## Compatibility note
This method will never work on unrooted Android devices due to the fact that the Authy app only trusts root certificates from the system store and rooting being needed to add certificates to the system store. If you have a rooted Android device and would like to use this guide, add the mitmproxy certificate to the system store instead, and you should be able to follow this guide normally. The reason this works on iOS is that iOS treats system root CAs and user-installed root CAs the same by default, and unless an app uses SSL pinning or some other method to deny user-installed root CAs, it can be HTTPS intercepted via a MiTM attack without a jailbreak needed. If Twilio wants to patch this by implementing SSL pinning, they absolutely can.

## Other info
You can find some more information on the comments of this GitHub Gist: [https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93).

If something goes wrong while following this guide, please file a GitHub issue and I will look into it.

## Acknowledgments

* Thank you to [Ahmad Morningstar](https://github.com/AhmadMorningstar) for contributing the `script.py` conversion script and improving the documentation.

Note that this is a fork from https://github.com/AlexTech01/Authy-iOS-MiTM the owner of this respectable repo is https://github.com/AlexTech01 at 
