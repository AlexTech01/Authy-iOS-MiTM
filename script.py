import json
import qrcode
from PIL import Image  # Ensure Pillow is installed

def convert_to_aegis_uris(json_data):
    """Converts Authy-like JSON to Aegis-compatible otpauth:// URIs."""

    try:
        data = json.loads(json_data)
        tokens = data.get("decrypted_authenticator_tokens", [])
        uris = []
        names = [] #added names list

        for token in tokens:
            name = token.get("name")
            issuer = token.get("issuer")
            secret = token.get("decrypted_seed")
            digits = token.get("digits", 6)  # Default to 6 digits

            if name and secret:
                uri = f"otpauth://totp/{name.replace(':', '').replace(' ', '')}?secret={secret}&digits={digits}&algorithm=SHA1&period=30"
                if issuer:
                    uri += f"&issuer={issuer.replace(' ', '')}"
                uris.append(uri)
                names.append(name) #added name to names list

        return uris, names #return names list

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
        with open("data.json", "r") as f:
            json_data = f.read()
            uris, names = convert_to_aegis_uris(json_data)

            if "Error" in uris[0]: #handle errors
                print(uris[0])
                return

            for uri in uris:
                print(uri)

        user_input = input("Generate QR codes? (Y/n): ").lower()
        if user_input == "y":
            for i, uri in enumerate(uris):
                filename = f"qrcode_{names[i].replace(':', '_').replace(' ', '_')}.png" #using names list to create filename
                generate_qr_code(uri, filename)
                print(f"QR code generated: {filename}")

    except FileNotFoundError:
        print("Error: data.json not found. Please make a copy of your original Decrypted.json file and rename it to data.json. Must be in the same directory as this script and run it again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()