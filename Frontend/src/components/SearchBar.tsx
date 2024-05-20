import React from "react";
import { View, StyleSheet } from "react-native";
import { SearchBar } from "@rneui/themed";
import { Picker } from "@react-native-picker/picker";

interface SearchBarComponentProps {
  pickerItems: { label: string; value: string }[];
  search: string;
  setSearch: (search: string) => void;
  searchPicker: string;
  setSearchPicker: (criteria: string) => void;
}
const SearchBarComponent: React.FC<SearchBarComponentProps> = ({
  pickerItems,
  search,
  setSearch,
  searchPicker,
  setSearchPicker,
}) => {
  return (
    <View style={styles.view}>
      <Picker
        selectedValue={searchPicker}
        style={styles.picker}
        onValueChange={(itemValue: string) => setSearchPicker(itemValue)}
      >
        {pickerItems.map((item) => (
          <Picker.Item key={item.value} label={item.label} value={item.value} />
        ))}
      </Picker>
      <SearchBar
        placeholder="Buscar"
        onChangeText={(value) => setSearch(value)}
        value={search}
        platform="android"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  view: {
    margin: 10,
  },
  picker: {
    backgroundColor:"#EAEAEA",
    height: 50,
    width: "100%",
  },
});

export default SearchBarComponent;
