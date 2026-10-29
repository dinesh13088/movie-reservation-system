import { createApiClient, MOVIES_BASE_URL } from "./createApiClient";

// Movies Service client (port 8002)
export default createApiClient(MOVIES_BASE_URL);