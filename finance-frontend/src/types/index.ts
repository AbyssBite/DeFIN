export type TransactionType = "inflow" | "outflow";

export interface Transaction {
    id: string;
    user_id: string;
    email: string;
    description?: string;
    amount: number;
    trx_type: TransactionType;
    created_at: string;
    is_owner: boolean;
}

export interface User {
    id: string;
    email: string;
    is_active: boolean;
}
