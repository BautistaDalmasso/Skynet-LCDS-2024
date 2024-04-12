export interface ICreateUser {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

export interface IUser {
  firstName: string;
  lastName: string;
  email: string;
  dni?: string;
}

export interface ILoginResponse {
  access_token: string;
  user: IUser;
  detail?: string;
}

export interface ILogin {
  email: string;
  password: string;
}

export interface IUpdateKey {
  publicRSA: string;
  deviceUID: number;
}

export interface IChallenge {
  challenge: string;
  detail?: string;
}

export interface IVerifyChallenge {
  email: string;
  deviceUID: number;
  challenge: number[];
}

export interface IUpdateUserDNI {
  dni: string;
}

export interface IDeviceUIDResponse {
    deviceUID: number;
}