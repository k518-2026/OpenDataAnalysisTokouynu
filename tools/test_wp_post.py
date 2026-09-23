"""
Standalone WordPress Email Posting Connectivity Test for OpenDataAnalysisTokouynu.
Validates SMTP authentication and WordPress Post by Email delivery without running full analysis.
"""
from __future__ import annotations

from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
import logging
import os
from pathlib import Path
import smtplib
import sys

# Ensure UTF-8 output on all platforms
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TestWPPost")


def mask_secret(val: str) -> str:
    """Masks sensitive strings for safe diagnostic logging."""
    if not val:
        return "<NOT SET>"
    if len(val) <= 4:
        return "****"
    return val[:2] + "*" * (len(val) - 4) + val[-2:]


def test_wp_post():
    logger.info("================================================================")
    logger.info("🧪 WordPress Post by Email Connectivity Test")
    logger.info("================================================================")

    # 1. Read environment variables
    wp_post_email = os.getenv("WP_POST_EMAIL", "").strip()
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").replace(" ", "").strip()
    wp_site_url = os.getenv("WP_SITE_URL", "https://seda68.wordpress.com").strip()

    logger.info(f"Target WordPress Site : {wp_site_url}")
    logger.info(f"Target Post by Email  : {mask_secret(wp_post_email)}")
    logger.info(f"SMTP Server           : {smtp_host}:{smtp_port}")
    logger.info(f"SMTP User (Sender)    : {mask_secret(smtp_user)}")
    logger.info(f"SMTP Pass             : {'[Configured - ' + str(len(smtp_pass)) + ' chars]' if smtp_pass else '<NOT SET>'}")

    # 2. Validate configuration
    missing = []
    if not wp_post_email:
        missing.append("WP_POST_EMAIL (WordPress.com Post by Email address)")
    if not smtp_user:
        missing.append("SMTP_USER (Sender email address, e.g. your Gmail)")
    if not smtp_pass:
        missing.append("SMTP_PASS (16-digit Google App Password)")

    if missing:
        logger.error("❌ Configuration Error: The following required secrets are missing:")
        for m in missing:
            logger.error(f"   - {m}")
        logger.error("👉 Please register them under GitHub Settings -> Secrets and variables -> Actions.")
        sys.exit(1)

    # 3. Create a test sample image
    test_img_path = Path(__file__).resolve().parent / "sample_test_chart.png"
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot([2021, 2022, 2023, 2024, 2025], [10, 25, 45, 70, 95], marker="o", color="#1e3a8a", linewidth=2.5)
        ax.set_title("Test Pipeline Connectivity - Empirical Chart", fontsize=12, fontweight="bold")
        ax.set_xlabel("Year")
        ax.set_ylabel("Index")
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.tight_layout()
        fig.savefig(test_img_path, dpi=120)
        plt.close(fig)
        logger.info("Generated sample verification chart image.")
    except Exception as e:
        logger.warning(f"Could not generate sample chart (continuing without image): {e}")

    # 4. Construct test MIME email
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[TEST] OpenDataAnalysisTokouynu Connectivity Verification ({now_str})"

    html_content = f"""[status publish] [category Test, Open Data Analysis] [tags Verification, System Test]

<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; color: #1e293b;">
  <div style="background: #1e3a8a; color: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h2 style="margin: 0; color: #ffffff;">🎉 WordPress Email Posting Test Successful!</h2>
    <p style="margin: 8px 0 0 0; color: #93c5fd; font-size: 0.9em;">Dispatched from GitHub Actions to {wp_site_url}</p>
  </div>

  <p>This is an automated connectivity test message dispatched from the <strong>OpenDataAnalysisTokouynu</strong> system.</p>
  
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; margin: 20px 0;">
    <h4 style="margin-top: 0; color: #0284c7;">Transmission Details:</h4>
    <ul style="margin-bottom: 0; font-size: 0.95em; color: #475569;">
      <li><strong>Dispatch Timestamp:</strong> {now_str}</li>
      <li><strong>Target Blog:</strong> <a href="{wp_site_url}">{wp_site_url}</a></li>
      <li><strong>Delivery Protocol:</strong> Post by Email via SMTP TLS</li>
    </ul>
  </div>

  <p>If you see this post published on your WordPress blog, the SMTP credentials and WordPress Post by Email pipeline are <strong>fully functional</strong>!</p>
</div>
"""

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = wp_post_email

    # Alternative part
    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText("This is an HTML test message from OpenDataAnalysisTokouynu.", "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach sample image if exists
    if test_img_path.exists():
        with open(test_img_path, "rb") as f:
            img = MIMEImage(f.read(), name="sample_test_chart.png")
            img.add_header("Content-Disposition", "attachment", filename="sample_test_chart.png")
            msg.attach(img)

    # 5. Connect and send via SMTP
    try:
        logger.info(f"Connecting to SMTP host {smtp_host}:{smtp_port}...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=25)
        server.set_debuglevel(1)  # Detailed SMTP protocol debug trace

        logger.info("Issuing EHLO and STARTTLS...")
        server.ehlo()
        server.starttls()
        server.ehlo()

        logger.info(f"Authenticating with SMTP server as '{mask_secret(smtp_user)}'...")
        server.login(smtp_user, smtp_pass)
        logger.info("✅ SMTP Authentication Succeeded!")

        logger.info(f"Sending test email to WordPress Post by Email ({mask_secret(wp_post_email)})...")
        send_errs = server.sendmail(smtp_user, [wp_post_email], msg.as_string())
        server.quit()

        if send_errs:
            logger.warning(f"⚠️ SMTP delivery returned recipient warnings: {send_errs}")
        else:
            logger.info("================================================================")
            logger.info("🎉 SUCCESS! Test email has been accepted by the SMTP server.")
            logger.info(f"👉 Please check your blog: {wp_site_url}")
            logger.info("(WordPress usually publishes incoming emails within 1-3 minutes)")
            logger.info("================================================================")

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication Failed (535): {e}")
        logger.error("👉 Please ensure you are using a 16-character Google 'App Password', NOT your regular Gmail password.")
        logger.error("👉 Visit: https://myaccount.google.com/apppasswords")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ SMTP Transmission Failed: {e}")
        sys.exit(1)
    finally:
        if test_img_path.exists():
            test_img_path.unlink()


if __name__ == "__main__":
    test_wp_post()
