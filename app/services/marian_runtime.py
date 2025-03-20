# app/services/marian_runtime.py
import os
import asyncio

class MarianRuntime:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.process = None
        
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
        
        
        # Build the command to run marian-decoder.
        # The typical command is:
        # marian-decoder -m <model_file> -v <vocab_file> <vocab_file> -c <decoder_config>
        cmd = f"marian-decoder -m {model_file} -v {vocab_file} {vocab_file} -c {decoder_config}"
        
        # Start the process asynchronously.
        self.process = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def translate(self, text: str) -> str:
        if self.process is None:
            await self.start()
        # Send the text (followed by a newline) to the process.
        self.process.stdin.write(text.encode('utf-8') + b'\n')
        await self.process.stdin.drain()
        # Read a single line of output.
        output = await self.process.stdout.readline()
        return output.decode('utf-8').strip()

    async def stop(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None

