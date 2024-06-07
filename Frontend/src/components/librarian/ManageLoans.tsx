import React, { useState } from "react";
import { View, Text, StyleSheet } from "react-native";
import Constants from "expo-constants";
import { TouchableOpacity } from "react-native-gesture-handler";
import ScanReturnedBook from "./BarcodeScanningScreens/ScanReturnedBook";
import { useFocusEffect } from "@react-navigation/native";
import ScanForLoan from "./BarcodeScanningScreens/ScanForLoan";

const ManageLoans = () => {
  const [scanningReturnedBook, setScanningReturnedBook] = useState(false);
  const [scanningForLoan, setScanningForLoan] = useState(false);

  useFocusEffect(
    React.useCallback(() => {
      setScanningReturnedBook(false);
      setScanningForLoan(false);

      return () => {};
    }, []),
  );

  if (scanningReturnedBook) {
    return (
      <ScanReturnedBook
        onBookReturnFinished={() => setScanningReturnedBook(false)}
      />
    );
  }

  if (scanningForLoan) {
    return <ScanForLoan onBookLoanFinished={() => setScanningForLoan(false)} />;
  }

  return (
    <View style={styles.contentContainer}>
      <Text style={styles.title}>Gestión de Préstamo</Text>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.button}
          onPress={() => setScanningReturnedBook(true)}
        >
          <Text style={styles.buttonText}>Escanear Libro Devuelto</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.button}
          onPress={() => setScanningForLoan(true)}
        >
          <Text style={styles.buttonText}>
            Escanear QR y Libro para Préstamo
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  contentContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  buttonContainer: {
    justifyContent: "center",
  },
  button: {
    backgroundColor: "#9ACD32",
    borderRadius: 5,
    padding: 15,
    marginHorizontal: 10,
    marginVertical: 5,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    textAlign: "center",
  },
});

export default ManageLoans;