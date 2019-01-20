
from googleapiclient import discovery
from googleapiclient import errors
import numpy as np
from skimage.io import imread
import sys
def predict_json(project, model, instances, version=None):
    """Send json data to a deployed model for prediction.

    Args:
        project (str): project where the Cloud ML Engine Model is deployed.
        model (str): model name.
        instances ([Mapping[str: Any]]): Keys should be the names of Tensors
            your deployed model expects as inputs. Values should be datatypes
            convertible to Tensors, or (potentially nested) lists of datatypes
            convertible to tensors.
        version: str, version of the model to target.
    Returns:
        Mapping[str: any]: dictionary of prediction results defined by the
            model.
    """
    # Create the ML Engine service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    service = discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)
    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']

# convert flattened list to a 2d list with given shape
def convert_2Darray(list,img_width,img_height):
    array = np.asarray(list)
    array = np.reshape(array,(img_width,img_height,4))
    converted_array = np.zeros(shape = (img_width,img_height))
    for row in range(len(array)):
        for col in range(len(array[row])):
            # weighed average of rgb colors to convert grayscale 
            converted_array[row][col] = .3 * array[row][col][0] + .59 * array[row][col][1] + .11 * array[row][col][2]
    return converted_array.tolist()

# send request to model hosted on Google ML engine
def send_request(img,img_width,img_height):
    img = convert_2Darray(img,img_width,img_height)
    dict = predict_json('cbis-ddsm-cnn','MammoWebApp_Model',[[img]])
    classes = dict[0]['output']
    # find the class with the highest probability 
    prediction = np.argmax(classes)
    return {'prediction':int(prediction)}