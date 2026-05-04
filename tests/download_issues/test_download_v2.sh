#!/usr/bin/env bash
set -euo pipefail

DEFAULT_BASE_URL="http://localhost:5001/"
BASE_URL="$DEFAULT_BASE_URL"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -b|--base-url)
            if [[ -z "${2:-}" ]]; then
                echo "ERROR: Missing value for $1" >&2
                exit 1
            fi
            BASE_URL="$2"
            shift 2
            ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            echo "Usage: $0 [--base-url URL]" >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="${BASE_URL}liwo.ws/Maps.asmx/DownloadZipFileDataLayers"

download_test() {
    local name="$1"
    local layers="$2"
    local output_path="${SCRIPT_DIR}/${name}"

    if [[ -e "$output_path" ]]; then
        echo "ERROR: Expected output file not to exist: $output_path" >&2
        exit 1
    fi

    http_code=$(curl -s -o "$output_path" -w "%{http_code}" \
        -X POST "$URL" \
        -H "Content-Type: application/json" \
        -d "{\"layers\": \"${layers}\", \"name\": \"${name}\"}")

    if [[ "$http_code" -ne 200 ]]; then
        rm -f "$output_path"
        echo "ERROR: Unexpected status code: $http_code" >&2
        exit 1
    fi

    if [[ ! -e "$output_path" ]]; then
        echo "ERROR: Download file was not created: $output_path" >&2
        exit 1
    fi

    size_bytes=$(wc -c < "$output_path")
    size_mb=$(awk "BEGIN {printf \"%.2f\", $size_bytes / 1048576}")
    echo "Saved ${size_mb} megabytes to ${output_path}"

    rm -f "$output_path"
    echo "downloaded ${name}"
}

test_download_small() {
    echo "testing download_small"
    download_test "test_download_small.zip" "MaximaleWaterdiepteNederland_Kaart1"
}

test_download_large() {
    echo "testing download_large"
    download_test "test_download_large.zip" "MaximaleWaterdiepteNederland_Kaart5"
}

test_download_small
test_download_large
