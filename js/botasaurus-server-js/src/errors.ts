import { isNullish } from "./null-utils"

class JsonHTTPResponseWithMessage extends Error {
  body: { message: any };
  status: number;
  headers: { [key: string]: any };

  constructor(body: any = null, status: number = 400, headers: { [key: string]: any } = {}) {
    if (isNullish(body)) {
      throw new Error('body must not be null');
    }    
    super(body);
    this.body = { message: body };
    this.status = status;
    this.headers = {
      ...headers,
      "Content-Type": "application/json",
    };
  }
}


export { JsonHTTPResponseWithMessage}