# Description: AI model logic for use in the AI agents in the 'Apples to Apples' game.

# Standard Libraries
import os
import logging
from dataclasses import dataclass
import numpy as np

# Third-party Libraries
from gensim.models import KeyedVectors
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '3' # Suppress TensorFlow logging
import keras.api._v2.keras as keras
from keras.models import Sequential
from keras.layers import Dense, Activation, LeakyReLU, ELU
from keras.layers import Dropout, BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping

# Local Modules
from source.apples import GreenApple, RedApple
from source.agent import Agent


@dataclass
class ModelData:
    green_apples: list[GreenApple]
    red_apples: list[RedApple]
    winning_red_apples: list[RedApple]

    def __post_init__(self) -> None:
        logging.debug(f"Created ModelData object: {self}")

    def __str__(self) -> str:
        return f"ModelData(green_apples={[apple.__adjective for apple in self.green_apples]}, red_apples={[apple.get_noun() for apple in self.red_apples]}, " \
               f"winning_red_apples={[apple.get_noun() for apple in self.red_apples]})"

    def __repr__(self) -> str:
        return f"ModelData(green_apples={[apple.__adjective for apple in self.green_apples]}, red_apples={[apple.get_noun() for apple in self.red_apples]}, " \
               f"winning_red_apples={[apple.get_noun() for apple in self.red_apples]})"

    def to_dict(self) -> dict:
        return {
            "green_apples": [apple.__adjective for apple in self.green_apples],
            "red_apples": [apple.get_noun() for apple in self.red_apples],
            "winning_red_apples": [apple.get_noun() for apple in self.winning_red_apples]
        }


class Model():
    """
    Base class for the AI models.
    """
    def __init__(self, judge: Agent, vector_size: int, pretrained_model: str, pretrain: bool) -> None:
        # Initialize the model attributes
        self._vector_base_directory = "./agents/"
        self._vector_size = vector_size
        self._judge: Agent = judge
        self._model_data: ModelData = ModelData([], [], [])
        self._judge_pairs = [] # Hopefully a better way to store the data.
        self._pretrained_model: str = pretrained_model # The name of the pretrained model (e.g., Literalist, Contrarian, Comedian)
        self._pretrain: bool = pretrain

        # Initialize slope and bias vectors
        self._slope_vector, self._bias_vector = self.__load_vectors(vector_size)

        # Learning attributes
        self._y_target: np.ndarray = np.zeros(shape=vector_size)  # Target score for the model
        self._learning_rate = 0.01  # Learning rate for updates

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(judge={self._judge}, model_data={self._model_data}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(judge={self._judge}, model_data={self._model_data}, "\
               f"slope_vector={self._slope_vector}, bias_vector={self._bias_vector}, "\
               f"learning_rate={self._learning_rate})"

    def get_slope_vector(self) -> np.ndarray:
        return self._slope_vector

    def get_bias_vector(self) -> np.ndarray:
        return self._bias_vector

    def __load_vectors(self, vector_size: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Load the slope and bias vectors from the pretrained model .npy files if they exist, otherwise initialize random values.
        """
        # Ensure the directory exists
        try:
            if not os.path.exists(self._vector_base_directory):
                os.makedirs(self._vector_base_directory, exist_ok=True)
                logging.info(f"Created vector directory: {self._vector_base_directory}")
            else:
                logging.info(f"Directory already exists: {self._vector_base_directory}")
        except OSError as e:
            logging.error(f"Error creating vector directory: {e}")

        # Define the file paths for the vectors
        slope_vector_file: str = f"{self._vector_base_directory}{self._pretrained_model}_slope.npy"
        bias_vector_file: str = f"{self._vector_base_directory}{self._pretrained_model}_bias.npy"

        # Load the vectors from the pretrained model
        try:
            # Check if the files exist
            if os.path.exists(slope_vector_file) and os.path.exists(bias_vector_file):
                slope_vector = np.load(slope_vector_file)
                bias_vector = np.load(bias_vector_file)
                logging.info(f"Loaded vectors from {slope_vector_file} and {bias_vector_file}")
            else: # If not, initialize random vectors
                slope_vector = np.random.rand(vector_size)
                bias_vector = np.random.rand(vector_size)
                logging.info("Initialized random vectors")
        # Handle any errors that occur
        except OSError as e:
            logging.error(f"Error loading vectors: {e}")
            slope_vector = np.random.rand(vector_size)
            bias_vector = np.random.rand(vector_size)

        return slope_vector, bias_vector

    def _save_vectors(self) -> None:
        """
        Save the slope and bias vectors to .npy files.
        """
        # Ensure the tmp directory exists
        tmp_directory = self._vector_base_directory + "tmp/"
        try:
            if not os.path.exists(tmp_directory):
                os.makedirs(tmp_directory, exist_ok=True)
                logging.info(f"Created tmp directory: {tmp_directory}")
            else:
                logging.info(f"Tmp directory already exists: {tmp_directory}")
        except OSError as e:
            logging.error(f"Error creating tmp directory: {e}")

        try:
            # If pretrain is True, save the vectors to the pretrained model files
            if self._pretrain:
                slope_file: str = f"{self._vector_base_directory}{self._pretrained_model}_slope.npy"
                bias_file: str = f"{self._vector_base_directory}{self._pretrained_model}_bias.npy"
                np.save(slope_file, self._slope_vector)
                np.save(bias_file, self._bias_vector)
                logging.info(f"Saved vectors to {slope_file} and {bias_file}")
            else: # Otherwise, save the vectors to the temporary model files
                tmp_slope_file = f"{tmp_directory}{self._pretrained_model}_slope_{self._judge.get_name()}-tmp.npy"
                tmp_bias_file = f"{tmp_directory}{self._pretrained_model}_bias_{self._judge.get_name()}-tmp.npy"
                np.save(tmp_slope_file, self._slope_vector)
                np.save(tmp_bias_file, self._bias_vector)
                logging.info(f"Saved vectors to {tmp_slope_file} and {tmp_bias_file}")
        except OSError as e:
            logging.error(f"Error saving vectors: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    # def __result_vector(self, green_apple_vector: np.ndarray, red_apple_vector: np.ndarray) -> np.ndarray:
    #     """
    #     Produces the resultant vector when you run through the algorithm
    #     """
    #     x = np.multiply(green_apple_vector, red_apple_vector)
    #     return np.multiply(self._slope_vector, x) + self._bias_vector

    # def _calculate_score(self, green_apple_vector, red_apple_vector) -> float:
    #     """
    #     Produces the score of the model for a combination of red and green cards.
    #     """
    #     return np.sum(self.__result_vector(green_apple_vector, red_apple_vector))

    def _calculate_score(self, green_apple_vector: np.ndarray, red_apple_vector: np.ndarray) -> float:
        """
        Produces the score of the model for a combination of red and green cards.
        """
        x = np.multiply(green_apple_vector, red_apple_vector)
        result_vector = np.multiply(self._slope_vector, x) + self._bias_vector
        return float(np.sum(result_vector))

    def train_model(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, winning_red_apple: RedApple, loosing_red_apples: list[RedApple]) -> None:
        """
        Train the model using pairs of green and red apple vectors.
        """
        raise NotImplementedError("Subclass must implement the 'train_model' method")

    # def choose_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[RedApple]) -> RedApple:
    #     """
    #     Choose a red card from the agent's hand to play (when the agent is a regular player).
    #     """
    #     raise NotImplementedError("Subclass must implement the 'choose_red_apple' method")

    def choose_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[RedApple]) -> RedApple:
        """
        Choose a red card from the agent's hand to play (when the agent is a regular player).
        This method applies the private linear regression methods to predict the best red apple.
        """
        # Set the green apple vector
        green_apple.set_adjective_vector(keyed_vectors)
        green_apple_vector = green_apple.get_adjective_vector()

        # Initialize the best score and best red apple
        best_red_apple: RedApple | None = None
        best_score: float = -np.inf

        # Set the red apple vectors and calculate the score
        for red_apple in red_apples:
            red_apple.set_noun_vector(keyed_vectors)
            red_apple_vector = red_apple.get_noun_vector()

            # Check that the green and red vectors are not None
            if green_apple_vector is None:
                raise ValueError("Green apple vector is None.")
            if red_apple_vector is None:
                raise ValueError("Red apple vector is None.")

            # Calculate the score
            score = self._calculate_score(green_apple_vector, red_apple_vector)

            # Update the best score and red apple
            if score > best_score:
                best_red_apple = red_apple
                best_score = score

        # Check if the best red apple was chosen
        if best_red_apple is None:
            raise ValueError("No red apple was chosen.")

        return best_red_apple

    def choose_winning_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[dict[str, RedApple]]) -> dict[str, RedApple]:
        """
        Choose the winning red card from the red cards submitted by the other agents (when the agent is the judge).
        """
        raise NotImplementedError("Subclass must implement the 'choose_winning_red_apple' method")



class LRModel(Model):
    """
    Linear Regression model for the AI agent.
    """
    def __init__(self, judge: Agent, vector_size: int, pretrained_model: str, pretrain: bool) -> None:
        super().__init__(judge, vector_size, pretrained_model, pretrain)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()

    def __linear_regression(self, x_vectors: np.ndarray, y_vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Linear regression algorithm for the AI agent.
        """
        assert(len(x_vectors) == len(y_vectors))

        # Initalize the sum variables
        n = float(len(x_vectors))
        sumx = np.zeros(self._vector_size)
        sumx2 = np.zeros(self._vector_size)
        sumxy = np.zeros(self._vector_size)
        sumy = np.zeros(self._vector_size)
        sumy2 = np.zeros(self._vector_size)

        # Calculate the sums
        for x, y in zip(x_vectors, y_vectors):
            sumx = np.add(sumx, x)
            sumx2 = np.add(sumx2, np.multiply(x, x))
            sumxy = np.add(sumxy, np.multiply(x, y))
            sumy = np.add(sumy, y)
            sumy2 = np.add(sumy2, np.multiply(y, y))

        # Calculate the denominators
        denoms: np.ndarray = np.full(self._vector_size, n) * sumx2 - np.multiply(sumx, sumx)

        # Calculate the slopes and intercepts
        ms = np.zeros(self._vector_size)
        bs = np.zeros(self._vector_size)

        # Avoid division by zero
        for i, denom in enumerate(denoms):
            if denom == 0.0:
                continue
            ms[i] = (n * sumxy[i] - sumx[i] * sumy[i]) / denom
            bs[i] = (sumy[i] * sumx2[i] - sumx[i] * sumxy[i]) / denom

        return ms, bs

    # def __update_parameters(self, green_apple_vectors, red_apple_vectors):
    #     """
    #     Update the slope and bias vectors based on the error.
    #     """
    #     print(self) #for testing purposes, of

    #     # Calculate the error
    #     y_pred = self.__linear_regression(green_apple_vectors, red_apple_vectors)
    #     error = self._y_target - y_pred

    #     # Update slope and bias vectors
    #     x = np.multiply(green_apple_vectors, red_apple_vectors)
    #     self._slope_vector += self._learning_rate * np.dot(error, x) # TODO - Change self._slope_vector to a vector, right now it's a scalar
    #     self._bias_vector += self._learning_rate * error

    #     # Update the target score based on the error
    #     self._y_target = self._y_target - error

    #     print(self)

    def train_model(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, winning_red_apple: RedApple, loosing_red_apples: list[RedApple]) -> None:
        """
        Train the model using pairs of green and red apple vectors.
        """
        # Set the green and red apple vectors
        green_apple.set_adjective_vector(keyed_vectors)
        winning_red_apple.set_noun_vector(keyed_vectors)

        for i, red in enumerate(loosing_red_apples):
            loosing_red_apples[i].set_noun_vector(keyed_vectors)

        # Add the new green and red apples to the model data
        # self.model_data.green_apples.append(new_green_apple)
        # self.model_data.red_apples.append(new_red_apple)

        self._judge_pairs.append((green_apple, winning_red_apple, 1.0))
        for red in loosing_red_apples:
            self._judge_pairs.append((green_apple, red, -1.0))

        # # Get the green and red apple vectors
        # green_apple_vectors = [apple.get_adjective_vector() for apple in self.model_data.green_apples]
        # red_apple_vectors = [apple.get_noun_vector() for apple in self.model_data.red_apples]

        # Calculate the target score
        # for green_apple_vector, red_apple_vector in zip(green_apple_vectors, red_apple_vectors):
        #     self.y_target = self.__linear_regression(green_apple_vector, red_apple_vector)
        #     self.__update_parameters(green_apple_vector, red_apple_vector)

        xs= []
        ys = []

        # an array of vectors of x and y data
        for pair in self._judge_pairs:
            g_vec = pair[0].get_adjective_vector()
            r_vec = pair[1].get_noun_vector()
            x_vec = np.multiply(g_vec, r_vec)
            y_vec = np.full(self._vector_size, pair[2])
            xs.append(x_vec)
            ys.append(y_vec)

        nxs = np.array(xs)
        nys = np.array(ys)

        self._slope_vector, self._bias_vector = self.__linear_regression(nxs, nys)

        # Save the updated slope and bias vectors
        # logging.debug(f"Updated slope vector: {self._slope_vector}")
        # logging.debug(f"Updated bias vector: {self._bias_vector}")
        self._save_vectors()
        logging.debug(f"Saved updated vectors")

        # Save the updated slope and bias vectors
        # logging.debug(f"Updated slope vector: {self._slope_vector}")
        # logging.debug(f"Updated bias vector: {self._bias_vector}")
        self._save_vectors()
        logging.debug(f"Saved updated vectors")

    # def choose_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[RedApple]) -> RedApple:
    #     """
    #     Choose a red card from the agent's hand to play (when the agent is a regular player).
    #     This method applies the private linear regression methods to predict the best red apple.
    #     """
    #     # Set the green apple vector
    #     green_apple.set_adjective_vector(keyed_vectors)
    #     green_apple_vector = green_apple.get_adjective_vector()

    #     # Initialize the best score and best red apple
    #     best_red_apple: RedApple | None = None
    #     best_score: float = -np.inf

    #     # Set the red apple vectors and calculate the score
    #     for red_apple in red_apples:
    #         red_apple.set_noun_vector(keyed_vectors)
    #         red_apple_vector = red_apple.get_noun_vector()

    #         # Check that the green and red vectors are not None
    #         if green_apple_vector is None:
    #             raise ValueError("Green apple vector is None.")
    #         if red_apple_vector is None:
    #             raise ValueError("Red apple vector is None.")

    #         score = self._calculate_score(green_apple_vector, red_apple_vector)

    #         if score > best_score:
    #             best_red_apple = red_apple
    #             best_score = score

    #     # Check if the best red apple was chosen
    #     if best_red_apple is None:
    #         raise ValueError("No red apple was chosen.")

    #     return best_red_apple

    def choose_winning_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[dict[str, RedApple]]) -> dict[str, RedApple]:
        """
        Choose the winning red card from the red cards submitted by the other agents (when the agent is the judge).
        This method applies the private linear regression methods to predict the winning red apple.
        """
        # Set the green and red apple vectors
        green_apple.set_adjective_vector(keyed_vectors)
        green_apple_vector = green_apple.get_adjective_vector()

        # Initialize variables to track the best choice
        winning_red_apple: dict[str, RedApple] | None = None
        best_score = np.inf

        # Iterate through the red apples to find the best one
        for red_apple_dict in red_apples:
            for _, red_apple in red_apple_dict.items():
                red_apple.set_noun_vector(keyed_vectors)
                red_apple_vector = red_apple.get_noun_vector()

                # Check that the green and red vectors are not None
                if green_apple_vector is None:
                    raise ValueError("Green apple vector is None.")
                if red_apple_vector is None:
                    raise ValueError("Red apple vector is None.")

                # Calculate the predicted score
                predicted_score = self.__linear_regression(green_apple_vector, red_apple_vector)

                # Evaluate the score difference using Euclidean distances
                score_difference = np.linalg.norm(predicted_score - self._y_target)

                if score_difference < best_score:
                    best_score = score_difference
                    winning_red_apple = red_apple_dict

                # # Calculate the score
                # score = self._calculate_score(green_apple_vector, red_apple_vector)

                # # Update the best score and red apple
                # if score > best_score:
                #     winning_red_apple = red_apple_dict
                #     best_score = score

        # Check if the winning red apple is None
        if winning_red_apple is None:
            raise ValueError("No winning red apple was chosen.")

        return winning_red_apple


class NNModel(Model):
    """
    Neural Network model for the AI agent.
    """
    def __init__(self, judge: Agent, vector_size: int, pretrained_model: str, pretrain: bool) -> None:
        super().__init__(judge, vector_size, pretrained_model, pretrain)

        # Define the neural network model architecture with two hidden layers
        self.model = Sequential([
            Dense(vector_size, input_dim=vector_size, activation="relu"), # Input layer
            # BatchNormalization(),
            # Dropout(0.5),
            Dense(vector_size, activation="relu"), # Hidden layer 1
            # BatchNormalization(),
            # Dropout(0.5),
            Dense(vector_size, activation="relu"), # Hidden layer 2
            # BatchNormalization(),
            # Dropout(0.5),
            Dense(vector_size)  # Output layer
        ])

        # Compile the model
        self.model.compile(optimizer=Adam(learning_rate=self._learning_rate), loss="mean_squared_error")

    def __forward_propagation(self, green_apple_vector, red_apple_vector) -> np.ndarray:
        """
        Forward propagation algorithm for the AI agent.
        """
        # y = mx + b, where x is the product of green and red apple vectors
        x = np.multiply(green_apple_vector, red_apple_vector)
        # y_pred = np.multiply(self._slope_vector, x) + self._bias_vector
        # return y_pred
        return self.model.predict(np.array([x]))[0]

    def __back_propagation(self, green_apple_vector, red_apple_vector):
        """
        Back propagation algorithm for the AI agent.
        """
        # # Calculate the error
        # y_pred = self.__forward_propagation(green_apple_vector, red_apple_vector)
        # error = self._y_target - y_pred

        # # Update rule for gradient descent
        # x = np.multiply(green_apple_vector, red_apple_vector)
        # self._slope_vector += self._learning_rate * np.dot(error, x)
        # self._bias_vector += self._learning_rate * error

        # # Update the target score based on the error
        # self._y_target = self._y_target - error
        x = np.multiply(green_apple_vector, red_apple_vector)
        self.model.train_on_batch(np.array([x]), np.array([self._y_target]))

    def train_model(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, winning_red_apple: RedApple, loosing_red_apples: list[RedApple]) -> None:
        """
        Train the model using pairs of green and red apple vectors.
        """
        # Set the green and red apple vectors
        green_apple.set_adjective_vector(keyed_vectors)
        winning_red_apple.set_noun_vector(keyed_vectors)

        # Add the new green and red apples to the model data
        self._model_data.green_apples.append(green_apple)
        self._model_data.red_apples.append(winning_red_apple)

        # Get the green and red apple vectors
        green_apple_vectors = [apple.get_adjective_vector() for apple in self._model_data.green_apples]
        red_apple_vectors = [apple.get_noun_vector() for apple in self._model_data.red_apples]

        # Calculate the target score
        for green_apple_vector, red_apple_vector in zip(green_apple_vectors, red_apple_vectors):
            self._y_target = self.__forward_propagation(green_apple_vector, red_apple_vector)
            self.__back_propagation(green_apple_vector, red_apple_vector)

        # Save the updated slope and bias vectors
        super()._save_vectors()
        logging.debug(f"Saved updated vectors")

    # def choose_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[RedApple]) -> RedApple:
    #     """
    #     Choose a red card from the agent's hand to play (when the agent is a regular player).
    #     This method applies the private neural network methods to predict the best red apple.
    #     """
    #     # Set the green vector
    #     green_apple.set_adjective_vector(keyed_vectors)
    #     green_apple_vector = green_apple.get_adjective_vector()

    #     # Initialize the best score and best red apple
    #     best_red_apple: RedApple | None = None
    #     best_score: float = -np.inf

    #     # Iterate through the red apples to find the best one
    #     for red_apple in red_apples:
    #         red_apple.set_noun_vector(keyed_vectors)
    #         red_apple_vector = red_apple.get_noun_vector()

    #         # Check that the green and red vectors are not None
    #         if green_apple_vector is None:
    #             raise ValueError("Green apple vector is None.")
    #         if red_apple_vector is None:
    #             raise ValueError("Red apple vector is None.")

    #         score = self._calculate_score(green_apple_vector, red_apple_vector)

    #         if score > best_score:
    #             best_red_apple = red_apple
    #             best_score = score

    #     # Check if the best red apple is None
    #     if best_red_apple is None:
    #         raise ValueError("No red apple was chosen.")

    #     return best_red_apple

    def choose_winning_red_apple(self, keyed_vectors: KeyedVectors, green_apple: GreenApple, red_apples: list[dict[str, RedApple]]) -> dict[str, RedApple]:
        """
        Choose the winning red card from the red cards submitted by the other agents (when the agent is the judge).
        This method applies the private neural network methods to predict the winning red apple.
        """
        # Set the green and red apple vectors
        green_apple.set_adjective_vector(keyed_vectors)
        green_apple_vector = green_apple.get_adjective_vector()

        # Initialize variables to track the best choice
        winning_red_apple: dict[str, RedApple] | None = None
        best_score = -np.inf

        for red_apple_dict in red_apples:
            for _, red_apple in red_apple_dict.items():
                red_apple.set_noun_vector(keyed_vectors)
                red_apple_vector = red_apple.get_noun_vector()

                # Check that the green and red vectors are not None
                if green_apple_vector is None:
                    raise ValueError("Green apple vector is None.")
                if red_apple_vector is None:
                    raise ValueError("Red apple vector is None.")

                # Calculate the predicted score
                predicted_score = self.__forward_propagation(green_apple_vector, red_apple_vector)

                # Evaluate the score difference using Euclidean distances
                score_difference = np.linalg.norm(predicted_score - self._y_target)

                if score_difference < best_score:
                    best_score = score_difference
                    winning_red_apple = red_apple_dict

                # # Calculate the score
                # score = self._calculate_score(green_apple_vector, red_apple_vector)

                # # Update the best score and red apple
                # if score > best_score:
                #     winning_red_apple = red_apple_dict
                #     best_score = score

        # Check if the winning red apple is None
        if winning_red_apple is None:
            raise ValueError("No winning red apple was chosen.")

        return winning_red_apple


# Define the mapping from user input to model type
model_type_mapping = {
    '1': LRModel,
    '2': NNModel
}


if __name__ == "__main__":
    pass
