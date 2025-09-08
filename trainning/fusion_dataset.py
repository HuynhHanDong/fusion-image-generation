import torch
import torchvision.transforms as T
from torch.utils.data import Dataset

class FusionDataset(Dataset):
    def __init__(self, base_dataset, modality="pair", transform=None):
        """
        base_dataset: any torchvision dataset (e.g., CIFAR10, CelebA, MNIST)
        modality: type of second input ("grayscale", "edge", "blur", "pair")
        transform: torchvision transforms applied to images
        """
        self.base_dataset = base_dataset
        self.modality = modality
        self.transform = transform

        # Edge detector (Sobel-like)
        self.edge_filter = torch.tensor([[[-1., -1., -1.],
                                          [-1.,  8., -1.],
                                          [-1., -1., -1.]]]).unsqueeze(0)

    def __len__(self):
        return len(self.base_dataset)

    def __getitem__(self, idx):
        img, _ = self.base_dataset[idx]

        if self.transform:
            img = self.transform(img)

        # Generate second modality
        if self.modality == "grayscale":
            img2 = img.mean(dim=0, keepdim=True).expand_as(img)  # RGB-like grayscale
        elif self.modality == "edge":
            img_gray = img.mean(dim=0, keepdim=True)
            img2 = torch.nn.functional.conv2d(
                img_gray.unsqueeze(0), self.edge_filter, padding=1
            ).squeeze(0)
            img2 = img2.expand_as(img)
        elif self.modality == "blur":
            blur = T.GaussianBlur(3, sigma=1.0)
            img2 = blur(img)
        elif self.modality == "pair":
            # Random second image from dataset
            rand_idx = torch.randint(0, len(self.base_dataset), (1,)).item()
            img2, _ = self.base_dataset[rand_idx]
            if self.transform:
                img2 = self.transform(img2)
        else:
            raise ValueError(f"Unknown modality type: {self.modality}")

        target = img  # Fusion target is usually original image
        return img, img2, target
