import argparse
import requests
from concurrent.futures import ThreadPoolExecutor
from statistics import median
import urllib3

# Function to fetch data from a URL
def fetch_url(url):
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return url, response.status_code, len(response.content)
    except (requests.exceptions.RequestException, ValueError):
        return url, None, None

def main(input_file, num_threads, num_outliers):
    # Disable the InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Read URLs from the specified file
    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file]

    # Number of threads to use
    num_threads = min(num_threads, len(urls))

    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(fetch_url, urls))

    # Calculate the median response size
    response_sizes = [size for _, _, size in results if size is not None]
    median_size = median(response_sizes)

    # Calculate the differences from the median
    differences = [(url, abs(size - median_size)) for url, _, size in results if size is not None]

    # Sort the URLs by the difference in size
    differences.sort(key=lambda x: x[1], reverse=True)

    # Output the top N outliers
    print(f"Top {num_outliers} Outliers:")
    for i, (url, diff) in enumerate(differences[:num_outliers]):
        print(f"{i + 1}. URL: {url}\n   Difference from Median Size: {diff} bytes\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find top outliers in a list of URLs.")
    parser.add_argument("input_file", help="Path to the file containing URLs.")
    parser.add_argument("--num_threads", type=int, default=10, help="Number of threads to use for fetching URLs.")
    parser.add_argument("--num_outliers", type=int, default=10, help="Number of top outliers to display.")
    args = parser.parse_args()
    
    main(args.input_file, args.num_threads, args.num_outliers)

