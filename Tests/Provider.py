from enum import Enum


class Provider(Enum):
    aws = "aws"
    azure = "azure"
    ow = "ow"
    google = "google"
    k8s = "kubernetes"
