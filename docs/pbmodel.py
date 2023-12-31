import os
import sys
import warnings

import keras.backend as K
import tensorflow as tf
tf.compat.v1.disable_v2_behavior()
from mrcnn.config import Config

warnings.filterwarnings('ignore', category=FutureWarning)
# suppress warning and error message tf
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Root directory of the project
ROOT_DIR = "D:/Tomato_Disease_Detection_MRCNN"
# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import model as modellib
from mrcnn import utils
import custom

K.clear_session()
K.set_learning_phase(0)
tf.compat.v1.global_variables_initializer()

##############################################################################
# Load model
##############################################################################

# Model Directory
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
DEFAULT_WEIGHTS = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
# Download COCO trained weights from Releases if needed
if not os.path.exists(DEFAULT_WEIGHTS):
    utils.download_trained_weights(DEFAULT_WEIGHTS)

##############################################################################
# Load configuration
##############################################################################

# Load Configuration Model
config = custom.CustomConfig()


# Override the training configurations with a few changes for inference.
class InferenceConfig(config.__class__):
    # Run detection on one image at a time
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

# Device to load the neural network on.
# Useful if you're training a model on the same
# machine, in which case use CPU and leave the
# GPU for training.
DEVICE = "/cpu:0"

# Inspect the model in training or inference modes
# values: 'inference' or 'training'
TEST_MODE = "inference"


##############################################################################
# Save entire model function
##############################################################################

def h5_to_pb(h5_model, output_dir, model_name, out_prefix="output_"):
    out_nodes = []
    for i in range(len(h5_model.outputs)):
        out_nodes.append(out_prefix + str(i + 1))
        tf.identity(h5_model.output[i], out_prefix + str(i + 1))
        
    sess = tf.compat.v1.Session()
    init_graph = sess.graph.as_graph_def()
    # init_graph = tf.Graph.as_graph_def()
    # main_graph = tf.compat.v1.graph_util.convert_variables_to_constants(sess, init_graph, out_nodes)
    main_graph = tf.compat.v1.graph_util.convert_variables_to_constants(sess, init_graph, out_nodes, variable_names_whitelist=None, variable_names_blacklist=None)
    with tf.compat.v1.gfile.GFile(os.path.join(output_dir, model_name), "wb") as filemodel:
        filemodel.write(main_graph.SerializeToString())
    print(f"pb model: {os.path.join(output_dir, model_name)}")


if __name__ == "__main__":
    config = InferenceConfig()
    config.display()
    # Create model in inference mode
    with tf.device(DEVICE):
        model = modellib.MaskRCNN(
            mode=TEST_MODE, model_dir=MODEL_DIR, config=config)

    # Set path to model weights
    weights_path = "D:/Tomato_Disease_Detection_MRCNN/logs/object20231005T1159/mask_rcnn_object_0010.h5"
    # Load weights
    print("Loading weights ", weights_path)
    model.load_weights(weights_path, by_name=True)
    model.keras_model.summary()

    # make folder for full model
    model_dir = os.path.join(ROOT_DIR, "Model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # save h5 full model
    name_model = os.path.join(model_dir, "mask_rcnn_custom.h5")
    if not os.path.exists(name_model):
        model.keras_model.save(name_model)
        print(f"save model: {name_model}")

    # export pb model
    pb_name_model = "mask_rcnn_landing.pb"
    h5_to_pb(model.keras_model, output_dir=model_dir, model_name=pb_name_model)
    K.clear_session()
    sys.exit()