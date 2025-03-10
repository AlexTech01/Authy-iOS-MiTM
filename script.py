import json
import qrcode
from PIL import Image
import os

def convert_to_uris(json_data, app_choice):
    """Converts Authy-like JSON to otpauth:// URIs based on app choice."""

    try:
        data = json.loads(json_data)
        tokens = data.get("decrypted_authenticator_tokens", [])
        uris = []
        names = []

        uri_formats = {
            "Aegis": "otpauth://totp/{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30&issuer={issuer}",
            "Google Authenticator": "otpauth://totp/{issuer}:{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30",
            "Microsoft Authenticator": "otpauth://totp/{issuer}:{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30",
            "2FA": "otpauth://totp/{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30&issuer={issuer}",
        }

        uri_format = uri_formats.get(app_choice)

        for token in tokens:
            name = token.get("name").replace(':', '_').replace(' ', '_')
            issuer = token.get("issuer").replace(' ', '_') if token.get("issuer") else ""
            secret = token.get("decrypted_seed")
            digits = token.get("digits", 6)

            if name and secret and uri_format:
                uri = uri_format.format(name=name, secret=secret, digits=digits, issuer=issuer)
                uris.append(uri)
                names.append(token.get("name"))

        return uris, names

    except json.JSONDecodeError:
        return ["Error: Invalid JSON input."], []
    except Exception as e:
        return [f"An unexpected error occurred: {e}"], []

def generate_qr_code(uri, filename):
    """Generates a QR code from a URI and saves it to a file."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def main():
    try:
        app_choices = ["Aegis", "Google Authenticator", "Microsoft Authenticator", "2FA"]
        print("Select your authenticator app:")
        for i, app in enumerate(app_choices):
            print(f"{i + 1}. {app}")

        while True:
            try:
                choice = int(input("Enter your choice (1, 2, etc.): ")) - 1
                if 0 <= choice < len(app_choices):
                    app_choice = app_choices[choice]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        with open("data.json", "r") as f:
            json_data = f.read()
            uris, names = convert_to_uris(json_data, app_choice)

            if "Error" in uris[0]:
                print(uris[0])
                return

            for uri in uris:
                print(uri)

        user_input = input("Generate QR codes? (Y/n): ").lower()
        if user_input == "y":
            folder_name = "Generated QR Codes into .png"
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            for i, uri in enumerate(uris):
                filename = os.path.join(folder_name, f"qrcode_{names[i].replace(':', '_').replace(' ', '_')}.png")
                generate_qr_code(uri, filename)
                print(f"QR code generated: {filename}")

    except FileNotFoundError:
        print("Error: data.json not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
