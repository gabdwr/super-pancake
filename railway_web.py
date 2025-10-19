#!/usr/bin/env python3
"""
Flask web server for Railway.app deployment with HTTP trigger endpoint.
This allows external cron services (like cron-job.org) to trigger datafetch on schedule.
"""

from flask import Flask, jsonify, request
import subprocess
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_datafetch():
    """
    HTTP endpoint to trigger datafetch via external cron service.
    This endpoint can be called by cron-job.org or similar services.
    """
    logger.info(f"🔔 Trigger endpoint called from {request.remote_addr}")

    try:
        # Run the datafetch script
        logger.info("🚀 Starting datafetch and filtration...")
        start_time = datetime.now()

        result = subprocess.run(
            ['python', 'run_datafetch_and_filtration.py'],
            capture_output=True,
            text=True,
            timeout=600,  # 10 min timeout (APIs can be slow)
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"✅ Datafetch completed in {duration:.1f}s with return code {result.returncode}")

        # Return response
        return jsonify({
            'status': 'success' if result.returncode == 0 else 'error',
            'timestamp': end_time.isoformat(),
            'duration_seconds': round(duration, 2),
            'returncode': result.returncode,
            'stdout_tail': result.stdout[-1000:] if result.stdout else '',  # Last 1000 chars
            'stderr_tail': result.stderr[-1000:] if result.stderr else ''
        }), 200 if result.returncode == 0 else 500

    except subprocess.TimeoutExpired:
        logger.error("❌ Datafetch timed out after 10 minutes")
        return jsonify({
            'status': 'error',
            'message': 'Script execution timed out after 10 minutes'
        }), 500

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'token-datafetch-cron'
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service info"""
    return jsonify({
        'service': 'Token Datafetch Cron Service',
        'endpoints': {
            '/trigger': 'POST/GET - Trigger datafetch script',
            '/health': 'GET - Health check',
            '/': 'GET - This info page'
        },
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Starting Flask server on port {port}")
    logger.info(f"📍 Available endpoints: /trigger, /health, /")

    # Railway sets PORT automatically
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False in production
    )
