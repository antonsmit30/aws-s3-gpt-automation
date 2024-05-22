import {AuthenticationDetails, CognitoUser, CognitoUserPool} from 'amazon-cognito-identity-js';
import userpool from '../userpool';
export const authenticate=(username, password)=>{
    const authData = {
        Username: username,
        Password: password
    }
    const authDetails = new AuthenticationDetails(authData);
    const userData = {
        Username: username,
        Pool: userpool
    }
    const cognitoUser = new CognitoUser(userData);
    return new Promise((resolve, reject)=>{
        cognitoUser.authenticateUser(authDetails, {
            onSuccess: data=>{
                resolve(data);
            },
            onFailure: err=>{
                reject(err);
            },
            newPasswordRequired: data=>{
                resolve(data);
            }
        })
    })
}

export const logout=()=>{
    const cognitoUser = userpool.getCurrentUser();
    if(cognitoUser){
        cognitoUser.signOut();
    }
}