"""Hosted entrypoint. Uses a single worker for bounded conversation sequencing."""
import os
import uvicorn
if __name__ == '__main__':
    os.environ['DG_HOSTED'] = 'true'
    uvicorn.run('backend.main:app', host='0.0.0.0', port=int(os.getenv('PORT','8000')), workers=1)
