from pathlib import Path
import pickle
import requests
import zipfile
from shutil import move

def download_file(url: str, output_path: Path | str | None = None, chunk_size: int = 8192) -> Path:
    """
    Download a file in chunks and return the Path to the downloaded file.
    If output_path is not provided, the filename will be extracted from the URL.
    
    Args:
        url: URL of the file to download
        output_path: Path where the file should be saved (optional)
        chunk_size: Size of chunks to download (default: 8192 bytes)
    
    Returns:
        Path: Path object pointing to the downloaded file
        
    Raises:
        requests.exceptions.RequestException: If download fails
        ValueError: If URL doesn't contain a filename and output_path is not provided
    """
    # If no output path is provided, extract filename from URL
    if output_path is None:
        # Get the filename from the URL
        filename = url.split('/')[-1].split('?')[0]  # Remove query parameters
        if not filename:
            raise ValueError("Could not determine filename from URL. Please provide output_path.")
        output_path = Path(__file__).parent.parent / "data" / filename
    else:
        output_path = Path(output_path)
    
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Download the file if it doesn't exist
    if not output_path.exists():
        print(f"Downloading file to {output_path}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        print("Download complete!")
    else:
        print(f"File already exists at {output_path}")
    
    return output_path



def extract_zip(zip_path: Path | str, extract_dir: Path | str) -> None:
    """
    Extract a zip file, skipping files that already exist with the same size.
    
    Args:
        zip_path: Path to the zip file
        extract_dir: Directory where files should be extracted
        
    Returns:
        None
    """
    # Convert to Path objects
    zip_path = Path(zip_path)
    extract_dir = Path(extract_dir)
    
    # Create extraction directory if it doesn't exist
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    print("Extracting files...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get list of files in archive
        for file_info in zip_ref.infolist():
            target_path = extract_dir / file_info.filename
            
            # Check if file needs to be extracted
            extract_file = True
            if target_path.exists():
                # Compare file sizes
                if target_path.stat().st_size == file_info.file_size:
                    extract_file = False
                    print(f"Skipping {file_info.filename} - already exists with same size")
            
            if extract_file:
                print(f"Extracting {file_info.filename}")
                zip_ref.extract(file_info, extract_dir)
    
    print("Extraction complete!")

def setup_data_dir():
    """
    Set up the data directory by downloading and extracting required files.
    
    Downloads the GenePT embedding file from Zenodo and extracts it into
    the 'data' directory. If files already exist, downloading and extraction
    will be skipped.
    """

    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Download URL
    url = "https://zenodo.org/records/10833191/files/GenePT_emebdding_v2.zip?download=1"
    zip_path = download_file(url)

    extract_zip(zip_path, data_dir)

    print("Setup finished!")

def get_gene_embeddings(model_name) -> dict:
    """
    Get the GenePT embeddings for a given model.
    """
    model_path_map = {
        "text-embedding-ada-002": "data/GenePT_emebdding_v2/GenePT_gene_embedding_ada_text.pickle",
        "text-embedding-3-large": "data/GenePT_emebdding_v2/GenePT_gene_protein_embedding_model_3_text.pickle.",
    }

    model_path = Path(__file__).parent.parent / model_path_map[model_name]
    with open(model_path, "rb") as f:
        return pickle.load(f)

def download_gdrive_file(url: str, output_path: Path | str ) -> Path:
    """
    Download a file from Google Drive using gdown and optionally rename/move it.
    
    Args:
        url: Google Drive sharing URL
        output_path: Path where the file should be saved (optional)
        
    Returns:
        Path: Path object pointing to the downloaded file
    """
    import gdown
    
    output_path = Path(output_path)
    if not output_path.exists():

        # Download to current directory first
        downloaded_path = gdown.download(url, fuzzy=True)
        if not downloaded_path:
            raise RuntimeError("Download failed")
        temp_path = Path(downloaded_path)    
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
        # Move file to final location if it's different from where it was downloaded
        if temp_path != output_path:
            print(f"Moving file to {output_path}...")
            move(str(temp_path), str(output_path))
    
    return output_path
