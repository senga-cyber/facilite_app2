export function getPositionOnce() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      return resolve(null); // on continue sans planter
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude
      }),
      () => resolve(null), // ignore erreurs
      { enableHighAccuracy: true, timeout: 7000 }
    );
  });
}
