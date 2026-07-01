import platform

from importlib import metadata

package_version = metadata.version("ucloud_sandbox")

default_headers = {
    "lang": "python",
    "lang_version": platform.python_version(),
    "package_version": metadata.version("ucloud_sandbox"),
    "publisher": "ucloud",
    "sdk_runtime": "python",
    "system": platform.system(),
}
