import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.util.Scanner;

public class ImageSteganography {
    public static void main(String[] args) {
        try {
            File imageFile = new File("C:\\Users\\abhin\\OneDrive\\Desktop\\Edunet intenship\\✅[80+] MS Dhoni 7 Looking at Sky Drawing Image _ Wallpaper HD (1026x1281) (2020).jpg");

            // Escaped backslashes

            if (!imageFile.exists()) {
                System.out.println("Error: Image file not found.");
                return;
            }

            BufferedImage img = ImageIO.read(imageFile);
            if (img == null) {
                System.out.println("Error: Unsupported image format.");
                return;
            }

            Scanner scanner = new Scanner(System.in);
            System.out.print("Enter secret message: ");
            String msg = scanner.nextLine();
            System.out.print("Enter a passcode: ");
            String password = scanner.nextLine();

            int width = img.getWidth();
            int height = img.getHeight();
            int maxPixels = width * height;

            if (msg.length() > maxPixels) {
                System.out.println("Error: Message too long for image capacity.");
                return;
            }

            int x = 0, y = 0, channel = 0;
            for (char ch : msg.toCharArray()) {
                if (y >= height) break;

                int pixel = img.getRGB(x, y);
                int[] rgb = {
                        (pixel >> 16) & 0xFF,
                        (pixel >> 8) & 0xFF,
                        pixel & 0xFF
                };

                rgb[channel] = ch & 0xFF;
                int newPixel = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2];
                img.setRGB(x, y, newPixel);

                channel = (channel + 1) % 3;
                if (channel == 0) {
                    x++;
                    if (x >= width) {
                        x = 0;
                        y++;
                    }
                }
            }

            File outputImage = new File("encryptedImage.jpg");
            if (!ImageIO.write(img, "jpg", outputImage)) {
                System.out.println("Error: Failed to save the encrypted image.");
                return;
            }

            System.out.println("Message encrypted and saved as 'encryptedImage.jpg'.");

            System.out.print("Enter passcode for decryption: ");
            String enteredPassword = scanner.nextLine();

            if (!enteredPassword.equals(password)) {
                System.out.println("Error: Incorrect passcode. Decryption failed.");
                return;
            }

            StringBuilder decryptedMessage = new StringBuilder();
            x = 0; y = 0; channel = 0;

            for (int i = 0; i < msg.length(); i++) {
                if (y >= height) break;

                int pixel = img.getRGB(x, y);
                int[] rgb = {
                        (pixel >> 16) & 0xFF,
                        (pixel >> 8) & 0xFF,
                        pixel & 0xFF
                };

                decryptedMessage.append((char) (rgb[channel] & 0xFF));

                channel = (channel + 1) % 3;
                if (channel == 0) {
                    x++;
                    if (x >= width) {
                        x = 0;
                        y++;
                    }
                }
            }

            if (decryptedMessage.length() > 0) {
                System.out.println("Decryption message: " + decryptedMessage.toString().trim());
            } else {
                System.out.println("Error: No message found or decryption failed.");
            }

        } catch (Exception e) {
            System.out.println("An unexpected error occurred. Please check your input and try again.");
        }
    }
}
