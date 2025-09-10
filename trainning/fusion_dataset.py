import torchvision.transforms as T
from torch.utils.data import Dataset
import random

class FusionDataset(Dataset):
    def __init__(self, base_dataset, transform=None):
        """
        base_dataset: any torchvision dataset (e.g., CIFAR10, CelebA, MNIST)
        transform: torchvision transforms applied to images
        """
        self.base_dataset = base_dataset
        self.transform = transform

    def __len__(self):
        return len(self.base_dataset)

    def __getitem__(self, idx):
        img1, _ = self.base_dataset[idx]

        # Pick a different random image
        idx2 = random.randint(0, len(self.base_dataset) - 1)
        while idx2 == idx:
            idx2 = random.randint(0, len(self.base_dataset) - 1)
        img2, _ = self.base_dataset[idx2]

        # Convert both to same size (required for blending)
        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)
        else:
            img1 = T.ToTensor()(img1)
            img2 = T.ToTensor()(img2)

        # # Create fusion target (alpha blend)
        # alpha = random.uniform(*self.alpha_range)
        # target = alpha * img1 + (1 - alpha) * img2
        # target = target.clamp(0, 1)  # keep valid pixel range

        return img1, img2
