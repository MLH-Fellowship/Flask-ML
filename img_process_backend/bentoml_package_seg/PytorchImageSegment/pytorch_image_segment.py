from typing import List, BinaryIO

from PIL import Image
import torch
from torch.autograd import Variable
from torchvision import transforms

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

            img = Image.open(fs)
            from torchvision import transforms
            preprocess = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            input_datas.append(preprocess(img))
        # input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model
        with torch.no_grad():
            # output = model(input_datas)['out'][0]
            output = self.artifacts.net(Variable(torch.stack(input_datas)))['out'][0]
        output_predictions = output.argmax(0)

        """
        outputs = self.artifacts.net(Variable(torch.stack(input_datas)))
        _, output_classes = outputs.max(dim=1)
        """

        # return [classes[output_class] for output_class in output_classes]
        return output_predictions
