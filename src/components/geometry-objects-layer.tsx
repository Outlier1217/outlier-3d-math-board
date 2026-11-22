"use client";

import { Line, Text } from "@react-three/drei";
import * as THREE from "three";
import { useGeometryStore } from "@/store/geometry-store";

type Vec3 = [number, number, number];

export default function GeometryObjectsLayer() {
  const objects = useGeometryStore((state) => state.objects);

  return (
    <group>
      {objects.filter((object) => object.visible).map((object) => {
        const p = object.params;
        const [cx, cy, cz] = p.center;
        const rotation = p.rotation * Math.PI / 180;

        if (
          object.kind === "circle" ||
          object.kind === "ellipse" ||
          object.kind === "parabola"
        ) {
          const points: Vec3[] = [];

          for (let i = 0; i <= 180; i++) {
            const t = i / 180 * Math.PI * 2;
            let x: number;
            let y: number;

            if (object.kind === "parabola") {
              const u = (i / 180 * 2 - 1) * p.extent;
              x = u;
              y = u * u / Math.max(0.05, 4 * p.a);
            } else {
              x = p.a * Math.cos(t);
              y = p.b * Math.sin(t);
            }

            points.push([
              cx + x * Math.cos(rotation) - y * Math.sin(rotation),
              cy + x * Math.sin(rotation) + y * Math.cos(rotation),
              cz,
            ]);
          }

          return (
            <group key={object.id}>
              <Line points={points} color={object.color} lineWidth={3} />
              <Text
                position={[cx + p.a + 0.15, cy, cz + 0.15]}
                fontSize={0.22}
                color={object.color}
                outlineWidth={0.02}
                outlineColor="#0F172A"
              >
                {object.name}
              </Text>
            </group>
          );
        }

        if (object.kind === "hyperbola") {
          return (
            <group key={object.id}>
              {[-1, 1].map((sign) => {
                const points: Vec3[] = [];

                for (let i = 0; i <= 120; i++) {
                  const t = i / 120 * p.extent;
                  const x = sign * p.a * Math.cosh(t);
                  const y = p.b * Math.sinh(t);

                  points.push([
                    cx + x * Math.cos(rotation) - y * Math.sin(rotation),
                    cy + x * Math.sin(rotation) + y * Math.cos(rotation),
                    cz,
                  ]);
                }

                return (
                  <Line
                    key={sign}
                    points={points}
                    color={object.color}
                    lineWidth={3}
                  />
                );
              })}
              <Text
                position={[cx + p.a, cy, cz + 0.2]}
                fontSize={0.22}
                color={object.color}
              >
                {object.name}
              </Text>
            </group>
          );
        }

        if (object.kind === "sphere") {
          return (
            <group key={object.id} position={p.center}>
              <mesh>
                <sphereGeometry args={[p.a, 40, 28]} />
                <meshPhysicalMaterial
                  color={object.color}
                  transparent
                  opacity={0.2}
                  side={THREE.DoubleSide}
                  depthWrite={false}
                />
              </mesh>
              <mesh>
                <sphereGeometry args={[p.a, 24, 16]} />
                <meshBasicMaterial
                  color={object.color}
                  wireframe
                  transparent
                  opacity={0.55}
                />
              </mesh>
              <Text
                position={[p.a + 0.15, 0, 0]}
                fontSize={0.22}
                color={object.color}
              >
                {object.name}
              </Text>
            </group>
          );
        }

        if (object.kind === "line") {
          const direction = new THREE.Vector3(...p.direction);

          if (direction.length() < 1e-8) return null;

          direction.normalize();

          const origin = new THREE.Vector3(...p.point);
          const start = origin.clone().addScaledVector(direction, -p.extent);
          const end = origin.clone().addScaledVector(direction, p.extent);

          return (
            <group key={object.id}>
              <Line
                points={[
                  start.toArray() as Vec3,
                  end.toArray() as Vec3,
                ]}
                color={object.color}
                lineWidth={3}
              />
              <Text
                position={end.toArray() as Vec3}
                fontSize={0.22}
                color={object.color}
              >
                {object.name}
              </Text>
            </group>
          );
        }

        if (object.kind === "plane") {
          const [a, b, c, d] = p.plane;
          const normal = new THREE.Vector3(a, b, c);

          if (normal.length() < 1e-8) return null;

          const denominator = a * a + b * b + c * c;
          const center = new THREE.Vector3(
            -d * a / denominator,
            -d * b / denominator,
            -d * c / denominator,
          );

          const helper = Math.abs(normal.z) < 0.9
            ? new THREE.Vector3(0, 0, 1)
            : new THREE.Vector3(0, 1, 0);

          const u = new THREE.Vector3()
            .crossVectors(normal, helper)
            .normalize();

          const v = new THREE.Vector3()
            .crossVectors(normal, u)
            .normalize();

          const s = p.extent;

          const corners = [
            center.clone().addScaledVector(u, -s).addScaledVector(v, -s),
            center.clone().addScaledVector(u, s).addScaledVector(v, -s),
            center.clone().addScaledVector(u, s).addScaledVector(v, s),
            center.clone().addScaledVector(u, -s).addScaledVector(v, s),
          ];

          const position = center.toArray() as Vec3;
          const quaternion = new THREE.Quaternion().setFromUnitVectors(
            new THREE.Vector3(0, 0, 1),
            normal.clone().normalize(),
          );

          return (
            <group key={object.id}>
              <mesh position={position} quaternion={quaternion}>
                <planeGeometry args={[s * 2, s * 2]} />
                <meshBasicMaterial
                  color={object.color}
                  transparent
                  opacity={0.2}
                  side={THREE.DoubleSide}
                  depthWrite={false}
                />
              </mesh>
              <Line
                points={[
                  ...corners.map((corner) => corner.toArray() as Vec3),
                  corners[0].toArray() as Vec3,
                ]}
                color={object.color}
                lineWidth={2}
              />
              <Text
                position={[position[0] + 0.2, position[1] + 0.2, position[2] + 0.2]}
                fontSize={0.22}
                color={object.color}
              >
                {object.name}
              </Text>
            </group>
          );
        }

        return null;
      })}
    </group>
  );
}
