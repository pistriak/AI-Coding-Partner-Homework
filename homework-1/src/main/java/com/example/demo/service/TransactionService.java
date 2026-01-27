package com.example.demo.service;

import com.example.demo.model.Transaction;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Currency;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;

@Service
public class TransactionService {
    private final Map<String, Transaction> transactions = new LinkedHashMap<>();
    private static final Pattern ACCOUNT_PATTERN = Pattern.compile("^ACC-[A-Za-z0-9]{5}$");

    public List<Transaction> getAllTransactions() {
        return new ArrayList<>(transactions.values());
    }

    public Optional<Transaction> getTransactionById(String id) {
        return Optional.ofNullable(transactions.get(id));
    }

    public Transaction createTransaction(Transaction request) {
        List<Map<String, String>> details = new ArrayList<>();

        BigDecimal amount = request.getAmount();
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            details.add(Map.of("field", "amount", "message", "Amount must be a positive number"));
        } else if (amount.scale() > 2) {
            details.add(Map.of("field", "amount", "message", "Amount must have at most 2 decimal places"));
        }

        String from = request.getFromAccount();
        String to = request.getToAccount();
        if (from == null || !ACCOUNT_PATTERN.matcher(from).matches()) {
            details.add(Map.of("field", "fromAccount", "message", "Account must follow format ACC-XXXXX (alphanumeric)"));
        }
        if (to == null || !ACCOUNT_PATTERN.matcher(to).matches()) {
            details.add(Map.of("field", "toAccount", "message", "Account must follow format ACC-XXXXX (alphanumeric)"));
        }

        String currencyCode = request.getCurrency();
        try {
            if (currencyCode == null || currencyCode.isBlank()) {
                throw new IllegalArgumentException("Invalid currency code");
            }
            Currency.getInstance(currencyCode.toUpperCase());
        } catch (Exception e) {
            details.add(Map.of("field", "currency", "message", "Invalid currency code"));
        }

        if (!details.isEmpty()) {
            throw new ValidationException(details);
        }

        Transaction tx = new Transaction();
        tx.setId(UUID.randomUUID().toString());
        tx.setFromAccount(request.getFromAccount());
        tx.setToAccount(request.getToAccount());
        tx.setAmount(request.getAmount());
        tx.setCurrency(request.getCurrency());
        tx.setType(request.getType());
        tx.setTimestamp(Instant.now());
        tx.setStatus("completed");
        transactions.put(tx.getId(), tx);
        return tx;
    }

    public BigDecimal getAccountBalance(String accountId) {
        BigDecimal balance = BigDecimal.ZERO;
        for (Transaction tx : transactions.values()) {
            if (!"completed".equalsIgnoreCase(tx.getStatus())) {
                continue;
            }
            String type = tx.getType() == null ? "" : tx.getType().toLowerCase(Locale.ROOT);
            if ("deposit".equals(type)) {
                if (accountId.equals(tx.getToAccount())) {
                    balance = balance.add(tx.getAmount());
                }
            } else if ("withdrawal".equals(type)) {
                if (accountId.equals(tx.getFromAccount())) {
                    balance = balance.subtract(tx.getAmount());
                }
            } else if ("transfer".equals(type)) {
                if (accountId.equals(tx.getFromAccount())) {
                    balance = balance.subtract(tx.getAmount());
                }
                if (accountId.equals(tx.getToAccount())) {
                    balance = balance.add(tx.getAmount());
                }
            }
        }
        return balance;
    }
}
