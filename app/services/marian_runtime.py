# app/services/marian_runtime.py
import os
import asyncio
import logging
from datetime import datetime

class MarianRuntime:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.process = None
        self.loaded_at = None
        self.model_key = os.path.basename(model_dir)
        # Only process one translation at a time
        self._translate_lock = asyncio.Lock()

    
    def win_to_wsl_path(self, win_path):
        """Convert Windows path to WSL path format to allow Marian NMT runtime"""
        if os.name == 'nt':  # Check if running on Windows
            # Handle full paths
            if ':' in win_path:
                drive, rest = os.path.splitdrive(win_path)
                drive = drive.replace(':', '')
                wsl_path = f"/mnt/{drive.lower()}{rest.replace('\\', '/')}"
                return wsl_path
            # Handle relative paths
            else:
                return win_path.replace('\\', '/')
        return win_path  # Return unchanged if not on Windows
    

    async def start(self):
        # Identify the required files in model_dir:
        files = os.listdir(self.model_dir)
        model_file = None
        vocab_file = None
        decoder_config = None

        for f in files:
            if f.endswith(".npz"):
                model_file = os.path.join(self.model_dir, f)
            if "vocab" in f and f.endswith(".yml"):
                vocab_file = os.path.join(self.model_dir, f)
            if "decoder" in f and f.endswith(".yml"):
                decoder_config = os.path.join(self.model_dir, f)
        
        if not model_file or not vocab_file or not decoder_config:
            raise FileNotFoundError("Required model files not found in " + self.model_dir)
        
        model_file_wsl = self.win_to_wsl_path(model_file)
        vocab_file_wsl = self.win_to_wsl_path(vocab_file)
        decoder_config_wsl = self.win_to_wsl_path(decoder_config)
        # Build the command to run marian-decoder.
        # The typical command is:
        # marian-decoder -m <model_file> -v <vocab_file> <vocab_file> -c <decoder_config>
        cmd = f"wsl marian-decoder -m {model_file_wsl} -v {vocab_file_wsl} {vocab_file_wsl} -c {decoder_config_wsl}"
        
        # Start the process asynchronously.
        try:
            self.process = await asyncio.create_subprocess_shell(
                cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self.loaded_at = datetime.now().isoformat()
            logging.info(f"Marian decoder started for {self.model_key}")
        except Exception as e:
            logging.error(f"Failed to start marian-decoder for {self.model_key}: {str(e)}")
            raise RuntimeError(f"Failed to start marian-decoder: {str(e)}")

    async def translate(self, text: str) -> str:
        if self.process is None:
            logging.info(f"Starting marian-decoder for {self.model_key} on demand")
            await self.start()

        async with self._translate_lock:
            try:
                # Add a newline to the input text
                input_text = text.strip() + '\n'
                
                # Write to stdin
                self.process.stdin.write(input_text.encode('utf-8'))
                await self.process.stdin.drain()
                
                # Read output
                output_line = await asyncio.wait_for(
                    self.process.stdout.readline(), 
                    timeout=120  # 2 minute timeout
                )
                
                # Decode and strip whitespace
                result = output_line.decode('utf-8').strip()
                return result
                
            except asyncio.TimeoutError:
                logging.error(f"Translation timeout for {self.model_key}")
                # Restart the process in case it's stuck
                await self.stop()
                await self.start()
                raise TimeoutError(f"Translation timed out for {self.model_key}")
                
            except Exception as e:
                logging.error(f"Translation error for {self.model_key}: {str(e)}")
                # Check if process is still alive
                if self.process and self.process.returncode is not None:
                    logging.error(f"Process died, restarting for {self.model_key}")
                    await self.start()
                raise RuntimeError(f"Translation error: {str(e)}")

    async def stop(self):
        """Stop the Marian decoder process"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
                logging.info(f"Marian decoder stopped for {self.model_key}")
            except asyncio.TimeoutError:
                logging.warning(f"Marian decoder did not terminate gracefully for {self.model_key}, killing")
                self.process.kill()
                await self.process.wait()
            finally:
                self.process = None
