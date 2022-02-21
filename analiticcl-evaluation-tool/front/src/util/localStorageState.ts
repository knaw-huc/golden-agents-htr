import { useEffect, useState } from "react";

const useLocalStorageState = (key: string, defaultValue: string) => {
  const [state, setState] = useState(
    () => window.localStorage.getItem(key) || defaultValue
  );

  useEffect(() => {
    window.localStorage.setItem(key, state);
  }, [key, state]);

  return [state, setState];
};

export default useLocalStorageState;
