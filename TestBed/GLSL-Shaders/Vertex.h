namespace shader_test {
    class Vertex {
    private:
        Vec3 position;
    public:
        Vertex() {
            position = Vec3();
        }

        Vertex(Vec3 position) {
            this->position = position;
        }

        Vec3 get_position() {
            return position;
        }

        void set_position(Vec3 position) {
            this->position = position;
        }
    };
}
