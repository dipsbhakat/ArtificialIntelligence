from flask import Flask, render_template_string
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    # Get Azure environment variables
    azure_vars = {k: v for k, v in os.environ.items() if 'AZURE' in k or 'WEBSITES' in k}
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Azure RAG Bot - Status</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .success { color: green; }
            .info { color: blue; }
            pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>🟢 Azure App Service - Flask Test</h1>
        <p class="success">✅ Flask is working on Azure App Service!</p>
        
        <h2>System Information</h2>
        <p><strong>Python Version:</strong> {{ python_version }}</p>
        <p><strong>Current Directory:</strong> {{ current_dir }}</p>
        <p><strong>Python Executable:</strong> {{ python_executable }}</p>
        
        <h2>Environment Variables</h2>
        <table>
            <tr><th>Variable</th><th>Value</th></tr>
            {% for key, value in azure_vars.items() %}
            <tr>
                <td>{{ key }}</td>
                <td>{{ value[:20] }}{% if value|length > 20 %}...{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>Directory Contents</h2>
        <pre>{{ directory_contents }}</pre>
        
        <h2>Next Steps</h2>
        <p class="info">✅ Basic Python/Flask is working</p>
        <p class="info">🔄 Ready to deploy Streamlit RAG bot</p>
    </body>
    </html>
    """
    
    # Get directory contents
    directory_contents = []
    try:
        directory_contents.append("=== Root Directory ===")
        for item in sorted(os.listdir('.')):
            directory_contents.append(f"  {item}")
        
        if os.path.exists('src'):
            directory_contents.append("\\n=== src Directory ===")
            for item in sorted(os.listdir('src')):
                directory_contents.append(f"  {item}")
    except Exception as e:
        directory_contents.append(f"Error listing directory: {e}")
    
    return render_template_string(html,
        python_version=sys.version,
        current_dir=os.getcwd(),
        python_executable=sys.executable,
        azure_vars=azure_vars,
        directory_contents="\\n".join(directory_contents)
    )

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Flask app is running'}

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('WEBSITES_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
