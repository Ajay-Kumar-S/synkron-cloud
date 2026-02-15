import os

# Check if running in cloud
CLOUD_MODE = os.environ.get("CLOUD_MODE") == "1"


def deep_root_analysis(cause):

    if CLOUD_MODE:
        # Lightweight cloud-safe version
        return (
            f"Root Cause Analysis (Cloud Mode):\n"
            f"Detected probable cause: {cause}.\n"
            "Further detailed AI analysis available in local deployment."
        )

    # Local AI mode
    try:
        from brain import generate_response

        prompt = f"Provide detailed engineering root cause analysis for: {cause}"
        return generate_response(prompt)

    except Exception:
        return f"Root Cause detected: {cause}"
