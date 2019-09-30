import {
  required,
  minLength,
  maxLength,
  minValue,
  number,
  regex,
  email,
  choices
} from 'react-admin';

export const validateTitle = [required(), minLength(2), maxLength(240)];
export const validateEmail = email();
export const validateAge = [number(), minValue(18)];
export const validateZipCode = regex(/^\d{5}$/, 'Must be a valid Zip Code');
export const validateSex = choices(['m', 'f'], 'Must be Male or Female');


export const normalizeTime = (value, previousValue) => {
  if (!value) {
    return value
  }
  const onlyNums = value.replace(/[^\d]/g, '')
  if (!previousValue || value.length > previousValue.length) {
    // typing forward
    if (onlyNums.length === 2) {
      return onlyNums + ':'
    }
    if (onlyNums.length === 4) {
      return onlyNums.slice(0, 2) + ':' + onlyNums.slice(2)
    }
  }
  if (onlyNums.length <= 2) {
    return onlyNums
  }
  if (onlyNums.length <= 4) {
    return onlyNums.slice(0, 2) + ':' + onlyNums.slice(2)
  }
  return onlyNums.slice(0, 2) + ':' + onlyNums.slice(2, 4)
}

export const verifyTime = (value) => {

if (value.slice(0,2) > 23) {
  return 'Erro: hora é um campo que aceita valores de 00 a 23';
}
if (value.slice(3,5) > 59) {
  return 'Erro: minutos vão de 00 a 59';
}

}