namespace shader_test {
    class Vec3 {
    private:
        float v[3];
    public:
        Vec3() {
            v[0] = v[1] = v[2] = 0.0f;
        }

        Vec3(float x, float y, float z) {
            v[0] = x;
            v[1] = y;
            v[2] = z;
        }

        float& x() {
            return v[0];
        }

        float& y() {
            return v[1];
        }

        float& z() {
            return v[2];
        }
    };
}
