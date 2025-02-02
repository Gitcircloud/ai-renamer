import json
import os
import sys

class Settings:
    def __init__(self):
        try:
            # If the application is run as a bundle
            if getattr(sys, 'frozen', False):
                application_dir = sys._MEIPASS # sys.MEIPASS points to the working directory of the exe file
                self.config_file = os.path.join(application_dir, 'config_template.json')
            
            # If the application is run as a script
            else:
                if os.path.exists('config.json'):
                    self.config_file = 'config.json' # for personal config, NOT pushed/packaged
                else:
                    self.config_file = 'config_template.json' # for default config, pushed/packaged

        except Exception as e:
            print(f"Error initializing settings: {e}")
            return {}
    
    def load(self):
        """Load settings from config file"""
        with open(self.config_file, 'r') as f:
            settings = json.load(f)
            
            # Get the current provider's base URL
            llm_provider = settings.get('llm_provider')
            api_base_url = settings.get(f"{llm_provider}_api_base_url")

            # Format the API base URL if it exists
            if api_base_url:
                
                # Add https:// if no protocol is specified
                if not api_base_url.startswith(('http://', 'https://')):
                    api_base_url = 'https://' + api_base_url
                
                # For Gemini,
                if llm_provider == 'gemini':
                    api_base_url = api_base_url.rstrip('/')

                    # If not official endpoint, check /v1 at the end
                    if not api_base_url == 'https://generativelanguage.googleapis.com/v1beta/openai':

                        if not api_base_url.endswith('/v1'):
                            api_base_url += '/v1'
                        settings.update({f"{llm_provider}_api_base_url": api_base_url})          
                
                # For other providers, ensure URL ends with /v1
                else: 
                    api_base_url = api_base_url.rstrip('/')
                    if not api_base_url.endswith('/v1'):
                        api_base_url += '/v1'
                    settings.update({f"{llm_provider}_api_base_url": api_base_url})
                
            return settings
        
    def save(self, settings):
        """Save settings to config file"""
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def get(self, key, default=None):
        """Get a setting value"""
        return self.load().get(key, default)
    
    def update(self, new_settings):
        """Update settings with new values"""
        current_settings = self.load()
        current_settings.update(new_settings)
        self.save(current_settings)