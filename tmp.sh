PLUGIN_DIR="plugins/bodhiext.common"
BODHILIB_VERSION="0.1.9"
poetry check --lock --directory ${PLUGIN_DIR}
sed "s/^bodhilib =.*/bodhilib = \"==${BODHILIB_VERSION}\"/" ${PLUGIN_DIR}/pyproject.toml > ${PLUGIN_DIR}/pyproject_temp.toml
mv ${PLUGIN_DIR}/pyproject_temp.toml ${PLUGIN_DIR}/pyproject.toml
poetry lock --no-update --directory ${PLUGIN_DIR}
poetry install --only main --only test --directory ${PLUGIN_DIR} --compile

