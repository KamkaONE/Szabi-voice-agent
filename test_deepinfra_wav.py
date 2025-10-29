#!/usr/bin/env python3
"""Test script to analyze DeepInfra WAV file format"""
import aiohttp
import asyncio
import struct

async def test_deepinfra_wav():
    api_key = "dBj3LhpsEy6lYb0LHK10jk2iSJwaBeLZ"
    api_url = "https://api.deepinfra.com/v1/openai/audio/speech"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "hexgrad/Kokoro-82M",
        "input": "Hello, testing audio format.",
        "voice": "af_heart",
        "response_format": "wav",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status != 200:
                print(f"Error: {response.status}")
                print(await response.text())
                return

            audio_bytes = await response.read()
            print(f"Total bytes received: {len(audio_bytes)}")

            # Parse WAV header
            if audio_bytes[:4] != b'RIFF':
                print("ERROR: Not a RIFF file!")
                return

            print("\n=== WAV Header Analysis ===")
            print(f"RIFF header: {audio_bytes[:4]}")

            file_size = struct.unpack('<I', audio_bytes[4:8])[0]
            print(f"File size (from header): {file_size + 8} bytes")

            print(f"WAVE marker: {audio_bytes[8:12]}")

            # Parse fmt chunk
            fmt_marker = audio_bytes[12:16]
            print(f"Format chunk marker: {fmt_marker}")

            fmt_size = struct.unpack('<I', audio_bytes[16:20])[0]
            print(f"Format chunk size: {fmt_size}")

            audio_format = struct.unpack('<H', audio_bytes[20:22])[0]
            print(f"Audio format: {audio_format} (1 = PCM)")

            num_channels = struct.unpack('<H', audio_bytes[22:24])[0]
            print(f"Number of channels: {num_channels}")

            sample_rate = struct.unpack('<I', audio_bytes[24:28])[0]
            print(f"Sample rate: {sample_rate} Hz")

            byte_rate = struct.unpack('<I', audio_bytes[28:32])[0]
            print(f"Byte rate: {byte_rate}")

            block_align = struct.unpack('<H', audio_bytes[32:34])[0]
            print(f"Block align: {block_align}")

            bits_per_sample = struct.unpack('<H', audio_bytes[34:36])[0]
            print(f"Bits per sample: {bits_per_sample}")

            # Find data chunk
            offset = 36
            while offset < len(audio_bytes) - 8:
                chunk_id = audio_bytes[offset:offset+4]
                chunk_size = struct.unpack('<I', audio_bytes[offset+4:offset+8])[0]

                if chunk_id == b'data':
                    print(f"\nData chunk found at offset {offset}")
                    print(f"Data chunk size: {chunk_size} bytes")
                    print(f"PCM data starts at byte: {offset + 8}")
                    print(f"PCM data size: {chunk_size} bytes")

                    # Calculate expected values
                    expected_samples = chunk_size // (bits_per_sample // 8) // num_channels
                    duration_seconds = expected_samples / sample_rate
                    print(f"Expected samples per channel: {expected_samples}")
                    print(f"Expected duration: {duration_seconds:.2f} seconds")

                    # Check if header size is 44 bytes
                    header_size = offset + 8
                    print(f"\n*** IMPORTANT: Header size is {header_size} bytes (not 44!) ***")

                    # Show first few bytes of PCM data
                    pcm_start = offset + 8
                    print(f"\nFirst 16 bytes of PCM data:")
                    print(" ".join(f"{b:02x}" for b in audio_bytes[pcm_start:pcm_start+16]))

                    # Check for non-zero data
                    pcm_data = audio_bytes[pcm_start:pcm_start+chunk_size]
                    non_zero_count = sum(1 for b in pcm_data if b != 0)
                    print(f"\nNon-zero bytes in PCM data: {non_zero_count}/{chunk_size} ({non_zero_count/chunk_size*100:.1f}%)")

                    # Find first non-zero byte
                    for i, b in enumerate(pcm_data):
                        if b != 0:
                            print(f"First non-zero byte at offset: {i}")
                            print(f"Bytes around first non-zero: {' '.join(f'{x:02x}' for x in pcm_data[max(0,i-8):i+8])}")
                            break
                    else:
                        print("WARNING: NO NON-ZERO BYTES FOUND IN ENTIRE PCM DATA!")

                    # Sample middle and end
                    mid_point = chunk_size // 2
                    print(f"\nMiddle 16 bytes of PCM data (offset {mid_point}):")
                    print(" ".join(f"{b:02x}" for b in pcm_data[mid_point:mid_point+16]))

                    print(f"\nLast 16 bytes of PCM data:")
                    print(" ".join(f"{b:02x}" for b in pcm_data[-16:]))

                    break

                offset += 8 + chunk_size

            print("\n=== Recommended Configuration ===")
            print(f"sample_rate={sample_rate}")
            print(f"num_channels={num_channels}")
            print(f"bits_per_sample={bits_per_sample}")
            print(f"Header size to strip: {header_size} bytes")

if __name__ == "__main__":
    asyncio.run(test_deepinfra_wav())