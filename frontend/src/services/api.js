import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const uploadDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || "Error uploading file";
    }
};

export const evaluateText = async (text) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/evaluate-text`, { text });
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || "Error evaluating text";
    }
};

export const verifyClaims = async (claims, searchContext = '') => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/verify-claims`, {
            claims,
            search_context: searchContext,
        });
        return response.data;
    } catch (error) {
        throw error.response?.data?.detail || "Error verifying claims";
    }
};