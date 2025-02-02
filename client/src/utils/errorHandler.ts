import { message } from 'antd';
import { AxiosError } from 'axios';
import { ApiResponse } from '../types';

export class AppError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'AppError';
  }
}

export const handleError = (error: AxiosError<ApiResponse> | AppError | Error) => {
  if (error instanceof AppError) {
    message.error(error.message);
    return;
  }

  if ((error as AxiosError).isAxiosError) {
    const axiosError = error as AxiosError<ApiResponse>;
    const errorMessage = axiosError.response?.data?.message || axiosError.message;
    message.error(errorMessage);
    return;
  }

  message.error(error.message || '未知错误');
};

export const createErrorHandler = (customHandler?: (error: any) => void) => {
  return (error: any) => {
    handleError(error);
    customHandler?.(error);
  };
}; 