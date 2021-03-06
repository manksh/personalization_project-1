import numpy as np 
import pandas as pd
from utils import loss_functions as lf

# TODO: should create a class for this model (Mohamed will take care of it)

def squared_error_gradient(M, U, V, W=None):
    """ 
    calculates the gradient and error of the simple MSE Loss function (unregularized)
    :param M: np.array | Numpy array that contains the rating matrix
    :param U: np.array | Numpy array that contains the user latent factors
    :param: np.array | Numpy array that contains the item latent facotrs
    :param: np.array | Numpy array that contains a weight matrix for the rating matrix (if bias is used)
    :return:
    """

    UV = np.dot(U,V)
    if W is None:
        E = np.subtract(M,UV)
    else:
        E = np.subtract(M,UV)
        E = E.multiply(W)
        
    J = 0.5 * np.nansum(np.square(E))
    # Error matrix
    
    return E, J

def simple_latent_factor_model(M,
                               latent_factors=10,
                               learning_rate=1e-6
                               ):
    """
    Calculates a latent factor model with give number of latent factors by gradient descent.
    Returns the ratings prediction matrix and the latent factor matrices U (users) and V (items)
    :param M:
    :param latent_factors:
    :param learning_rate:
    :return:
    """


    # Randomly initialize Matrix U and V
    m = M.shape[0]
    n = M.shape[1]
    U = pd.DataFrame(np.random.rand(m, latent_factors))
    V = pd.DataFrame(np.random.rand(latent_factors, n))

    # GD until convergence
    convergence = False
    i, J1 = 0, 1e6
    while not convergence:
        # compute Gradient and Loss
        E, J = squared_error_gradient(M, U, V)
        # fill Errors with 0 to ignore the values for prediction in the update
        E_upt = E.fillna(0)
        # update the matrices U and V by gradient descent
        U_update = np.dot(E_upt, np.transpose(V))
        V_update = np.transpose(np.dot(np.transpose(E_upt), U))
        U = U + learning_rate * U_update
        V = V + learning_rate * V_update

        print('Loss on iteration ' + str(i) + ': ' + str(J))

        # Convergence criteria
        if J / J1 > 0.9999:
            convergence = True
        else:
            J1 = J
        i += 1
    
    # TODO: to use in a separate function
    # calculate rating prediction

    R_hat = pd.DataFrame(np.dot(U, V))
    # print R_hat.shape

    return R_hat, U, V


def latent_factors_with_bias(M,
                            latent_factors=10, 
                            bias=None, 
                            bias_weights=None, 
                            regularization=0,
                            learning_rate=0.0001,
                            convergence_rate =0.1
                            ):
    # Calculates a latent factor model with give number of latent factors by gradient descent. 
    # Returns the ratings prediction matrix and the latent factor matrices U (users) and V (items)

    # Randomly initialize Matrix U and V
    m = M.shape[0]
    n = M.shape[1]
    U = pd.DataFrame(np.random.rand(m,latent_factors))
    V = pd.DataFrame(np.random.rand(latent_factors,n))
    
    if bias_weights: 
        W = M.copy()*0 + 1
        W = W.fillna(bias_weights)

    if bias: 
        M = M.fillna(bias)
    # GD until convergence
    convergence = False
    J1 = 1000000000
    i = 0
    while not(convergence): 
        # compute Gradient and Loss
        if bias: 
            E, J = squared_error_gradient(M,U,V,W)
        else: 
            E, J = squared_error_gradient(M,U,V)
        # fill Errors with 0 to ignore the values for prediction in the update
        E_upt = E.fillna(0)
        # update the matrixes U and V by gradient descent
        U_update = np.dot(E_upt,np.transpose(V))
        V_update = np.transpose(np.dot(np.transpose(E_upt),U))
        U_new = U*(1-learning_rate*regularization) + learning_rate*U_update
        V_new = V*(1-learning_rate*regularization) + learning_rate*V_update
        U = U_new
        V = V_new

        # print 'Loss on iteration ' + str(i) + ': ' + str(J)
        
        # Convergence criteria
        if abs(J-J1) < convergence_rate:
            convergence = True
        else:
            J1 = J
        i += 1
    
    # calculate rating prediciton

    R_hat = np.dot(U,V)

    return R_hat, U, V

def test_accuracy(M, R_hat):
    """
    :param M:
    :param R_hat:
    :return:
    """
    # returns the accuracy of the model predictions

    # turn probabilities into predictions
    prediction = R_hat[R_hat > 0.5] = 1
    prediction[prediction <= 0.5] = 0

    # calculate difference between prediction and real value
    accuracy = np.subtract(M, prediction).abs()

    # return accuracy value
    total_acc = accuracy.sum().sum()/M.count().sum()

    return total_acc


def hyper_parameter_tuning(data,
                           ModelTester,
                           latent_factors=5,
                           regularization=1,
                           bias=0.5,
                           bias_weights=0.2,

                           verbose=False):
    """
    :param data: df | rating matrix
    :param ModelTester: ModelTester obj | Object with validation and test set
    :param latent_factors: int |
    :param regularization:  float |
    :param bias: float |
    :param bias_weights: float |
    :return: list, list | two lists of ame and sme error
    """
    error_mse = []
    error_ame = []
    if type(latent_factors) == list:
        for l in latent_factors:
            predictions, U, V = latent_factors_with_bias(data,
                                                        latent_factors=l,
                                                        bias=bias,
                                                        bias_weights=bias_weights,
                                                        regularization=regularization,
                                                        )
            predictions = pd.DataFrame(predictions)
            predictions.columns = data.columns
            predictions.index = data.index
            ame = ModelTester.evaluate_valid(predictions, loss_func=lf.absolute_mean_error, verbose=verbose)
            mse = ModelTester.evaluate_valid(predictions, loss_func=lf.mean_squared_error, verbose=verbose)
            error_mse.append(mse)
            error_ame.append(ame)

    elif type(regularization) == list:
        for r in regularization:
            predictions, U, V = latent_factors_with_bias(data,
                                                        latent_factors=latent_factors,
                                                        bias=bias,
                                                        bias_weights=bias_weights,
                                                        regularization=r,
                                                        )
            predictions = pd.DataFrame(predictions)
            predictions.columns = data.columns
            predictions.index = data.index
            ame = ModelTester.evaluate_valid(predictions, loss_func=lf.absolute_mean_error, verbose=verbose)
            mse = ModelTester.evaluate_valid(predictions, loss_func=lf.mean_squared_error, verbose=verbose)
            error_mse.append(mse)
            error_ame.append(ame)

    elif type(bias) == list:
        for b in bias:
            predictions, U, V = latent_factors_with_bias(data,
                                                         latent_factors=latent_factors,
                                                         bias=b,
                                                         bias_weights=bias_weights,
                                                         regularization=regularization,
                                                         )
            predictions = pd.DataFrame(predictions)
            predictions.columns = data.columns
            predictions.index = data.index
            ame = ModelTester.evaluate_valid(predictions, loss_func=lf.absolute_mean_error, verbose=verbose)
            mse = ModelTester.evaluate_valid(predictions, loss_func=lf.mean_squared_error, verbose=verbose)
            error_mse.append(mse)
            error_ame.append(ame)

    elif type(bias_weights) == list:
        for bw in bias_weights:
            predictions, U, V = latent_factors_with_bias(data,
                                                        latent_factors=latent_factors,
                                                        bias=bias,
                                                        bias_weights=bw,
                                                        regularization=regularization,
                                                        )
            predictions = pd.DataFrame(predictions)
            predictions.columns = data.columns
            predictions.index = data.index
            ame = ModelTester.evaluate_valid(predictions, loss_func=lf.absolute_mean_error, verbose=verbose)
            mse = ModelTester.evaluate_valid(predictions, loss_func=lf.mean_squared_error, verbose=verbose)
            error_mse.append(mse)
            error_ame.append(ame)

    return error_mse, error_ame