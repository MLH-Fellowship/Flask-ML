from typing import List, BinaryIO

from PIL import Image
import torch
from torch.autograd import Variable
from torchvision import transforms
import matplotlib.pyplot as plt

import bentoml
from bentoml.frameworks.pytorch import PytorchModelArtifact
from bentoml.adapters import FileInput


classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


@bentoml.env(pip_packages=['torch', 'numpy', 'torchvision', 'scikit-learn'])
@bentoml.artifacts([PytorchModelArtifact('net')])
class PytorchImageSegment(bentoml.BentoService):

    @bentoml.utils.cached_property
    def transform(self):
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])

    @bentoml.api(input=FileInput(), batch=True)
    def predict(self, file_streams: List[BinaryIO]) -> List[str]:
        input_datas = []

        for fs in file_streams:
            """
            img = Image.open(fs).resize((32, 32))
            input_datas.append(self.transform(img))
            """
            img = Image.open(fs).convert("RGB")
            from torchvision import transforms
            preprocess = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[
                                     0.229, 0.224, 0.225]),
            ])

            input_datas.append(preprocess(img))
        # input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model
        with torch.no_grad():
            # output = model(input_datas)['out'][0]
            output = self.artifacts.net(
                Variable(torch.stack(input_datas)))['out'][0]
        output_predictions = output.argmax(0)

        # create a color pallette, selecting a color for each class
        palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])
        colors = torch.as_tensor([i for i in range(21)])[:, None] * palette
        colors = (colors % 255).numpy().astype("uint8")

        # plot the semantic segmentation predictions of 21 classes in each color
        r = Image.fromarray(
            output_predictions.byte().cpu().numpy()).resize(img.size)
        r.putpalette(colors)

        plt.imshow(r)
        plt.imsave(f'../assets/segmentingData/{fs.name}', r)

        # return [classes[output_class] for output_class in output_classes]
        return output_predictions
